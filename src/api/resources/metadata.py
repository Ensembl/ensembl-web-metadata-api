"""
See the NOTICE file distributed with this work for additional information
regarding copyright ownership.


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# import enum
import itertools
import logging

# from core.logging import InterceptHandler
import os

# import pytest
# import sqlalchemy
# import time
import timeit
import uuid
from datetime import datetime

from typing import Annotated, Any

from fastapi import Request, responses, Query, Path, Depends

from pydantic import ValidationError

from api.error_response import response_error_handler
from api.schemas.checksums import Checksum
from api.schemas.ftplinks import FTPLinks
from api.schemas.genome import (
    BriefGenomeDetails,
    GenomeDetails,
    DatasetAttributes,
    GenomeByKeyword,
    Release,
    GenomeGroupsResponse,
    GenomesInGroupResponse,
    GenomeCountsResponse,
)
from api.schemas.karyotype import Karyotype
from api.schemas.popular_species import PopularSpeciesGroup
from api.schemas.region_validation import RegionValidation
from api.schemas.statistics import GenomeStatistics, ExampleObjectList
from api.schemas.vep import VepFilePaths

from ensembl.production.metadata.api.models import Genome

from api.resources.redis import redis_cache
from api.resources.routes import router
from main import get_genome_adaptor, get_vep_adaptor, get_release_adaptor

GenomeAdaptorDep = Annotated[GenomeAdaptor, Depends(get_genome_adaptor)]
VepAdaptorDep = Annotated[VepAdaptor, Depends(get_vep_adaptor)]
ReleaseAdaptorDep = Annotated[ReleaseAdaptor, Depends(get_release_adaptor)]

# logging.getLogger().handlers = [InterceptHandler()]

from fastapi import APIRouter

router = APIRouter()

logging.info("Starting up")

from api.logic import (
    get_top_level_statistics_by_uuid,
    get_top_level_regions,
    assembly_region_iterator,
    create_assembly_region,
    get_organisms_group_count,
    create_organisms_group_count,
    get_attributes_by_genome_uuid,
    create_attributes_info,
    get_genome_by_uuid,
    create_genome_with_attributes_and_count,
    get_alternative_names,
    create_genome,
    create_assembly,
    create_taxon,
    create_organism,
    create_release,
    get_ftp_links,
    create_paths,
    get_brief_genome_details_by_uuid,
    is_valid_uuid,
    create_brief_genome_details,
    genome_assembly_sequence_region,
    create_genome_assembly_sequence_region,
    get_dataset_attributes,
    get_attributes_values_by_uuid,
    create_attribute_value,
    get_genomes_by_specific_keyword_iterator,
    get_vep_paths_by_uuid,
    release_iterator,
    get_genome_groups_by_reference,
    data_get_genomes_in_group,
    data_get_genome_counts,
)


@router.get("/genome/{genome_uuid}/stats", name="statistics")
@redis_cache("stats", arg_keys=["genome_uuid"])
async def get_metadata_statistics(
    adaptor: GenomeAdaptorDep, request: Request, genome_uuid: str
):
    try:
        top_level_stats = get_top_level_statistics_by_uuid(adaptor, genome_uuid)
        genome_stats = GenomeStatistics(_raw_data=top_level_stats)
        logging.debug(genome_stats.model_dump())
        return responses.JSONResponse({"genome_stats": genome_stats.model_dump()})
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_uuid}/karyotype", name="karyotype")
@redis_cache("karyotype", arg_keys=["genome_uuid"])
async def get_genome_karyotype(
    adaptor: GenomeAdaptorDep, request: Request, genome_uuid: str
):
    try:
        top_level_regions = get_top_level_regions(adaptor, genome_uuid)

        # Temporary hack for e.coli and remov when the correct schema/data is available in metadata-database
        if genome_uuid == "a73351f7-93e7-11ec-a39d-005056b38ce3":
            for tlr in top_level_regions:
                tlr["is_circular"] = True
        karyotype_response = Karyotype(top_level_regions=top_level_regions)
        return responses.JSONResponse(
            karyotype_response.model_dump()["top_level_regions"]
        )
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


@router.get("/popular_species", name="popular_species")
@redis_cache(key_prefix="popular_species")  # TTL defaults is 5 minutes
async def get_popular_species(adaptor: GenomeAdaptorDep, request: Request):
    try:
        popular_species_dict = get_organisms_group_count(adaptor, None)
        popular_species = popular_species_dict["organisms_group_count"]
        popular_species_response = PopularSpeciesGroup(
            _base_url=request.headers["host"], popular_species=popular_species
        )
        return responses.JSONResponse(popular_species_response.model_dump())
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


@router.get("/validate_location", name="validate_location")
def validate_region(
    adaptor: GenomeAdaptorDep, request: Request, genome_id: str, location: str
):
    try:
        rgv = RegionValidation(genome_uuid=genome_id, location_input=location)
        rgv.validate_region(adaptor)
        return responses.JSONResponse(rgv.model_dump())
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_id}/example_objects", name="example_objects")
@redis_cache("example_objects", arg_keys=["genome_id"])
async def example_objects(adaptor: GenomeAdaptorDep, request: Request, genome_id: str):
    try:
        attributes_info = get_attributes_by_genome_uuid(adaptor, genome_id, None)
        if attributes_info:
            example_objects = ExampleObjectList(
                example_objects=attributes_info["attributes_info"]
            )
            response_data = responses.JSONResponse(
                example_objects.model_dump()["example_objects"]
            )
        else:
            return response_error_handler(
                {
                    "status": 404,
                    "details": f"Could not find example objects for {genome_id}",
                }
            )
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


@router.get("/genome/{genome_uuid}/details", name="genome_details")
@redis_cache("details", arg_keys=["genome_uuid"])
async def get_genome_details(
    adaptor: GenomeAdaptorDep, request: Request, genome_uuid: str
):
    try:
        genome_details_dict = get_genome_by_uuid(adaptor, genome_uuid, None)

        if genome_details_dict:
            genome_details = GenomeDetails(**genome_details_dict)
            response_data = responses.JSONResponse(
                genome_details.model_dump(
                    exclude={
                        "release": {"is_current"},
                    }
                )
            )
        else:
            return response_error_handler(
                {"status": 404, "details": f"Could not find details for {genome_uuid}"}
            )
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


@router.get("/genome/{genome_uuid}/ftplinks", name="genome_ftplinks")
@redis_cache("ftplinks", arg_keys=["genome_uuid"])
async def get_genome_ftplinks(
    adaptor: GenomeAdaptorDep, request: Request, genome_uuid: str
):
    try:
        ftplinks_dict = get_ftp_links(adaptor, genome_uuid, "all", None)

        # This is temporary solution to hide regulation ftp links
        # It should be removed once the ftp links for regulation is fixed
        ftplinks_no_regulation = {}
        ftplinks_no_regulation["links"] = [
            link
            for link in sorted(ftplinks_dict["links"], key=lambda d: d["dataset_type"])
            if link["dataset_type"] != "regulation"
        ]

        ftplinks = FTPLinks(**ftplinks_no_regulation)
        return responses.JSONResponse(ftplinks.model_dump().get("links", []))
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_id_or_slug}/explain", name="genome_explain")
@redis_cache(key_prefix="explain", arg_keys=["genome_id_or_slug"])
async def explain_genome(
    adaptor: GenomeAdaptorDep, request: Request, genome_id_or_slug: str
):
    try:
        genome_details_dict = get_brief_genome_details_by_uuid(
            adaptor, genome_id_or_slug, None
        )
        if genome_details_dict:
            genome_details = BriefGenomeDetails(**genome_details_dict)
            response_dict = genome_details.model_dump(
                include={
                    "genome_id": True,
                    "genome_tag": True,
                    "scientific_name": True,
                    "species_taxonomy_id": True,
                    "common_name": True,
                    "is_reference": True,
                    "assembly": {"name", "accession_id"},
                    "release": {"name", "type"},
                    "type": True,
                    "latest_genome": True,
                }
            )
            response_data = responses.JSONResponse(response_dict, status_code=200)
        else:
            return response_error_handler(
                {"status": 404, "details": f"Could not explain {genome_id_or_slug}"}
            )
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


@router.get("/genome/{genome_uuid}/checksum/{region_name}", name="region_checksum")
async def get_region_checksum(
    adaptor: GenomeAdaptorDep, request: Request, genome_uuid: str, region_name: str
):
    try:
        region_checksum_dict = genome_assembly_sequence_region(
            db_conn=adaptor, genome_uuid=genome_uuid, sequence_region_name=region_name
        )
        region_checksum = Checksum(**region_checksum_dict)
        return responses.PlainTextResponse(region_checksum.md5)
    except ValidationError as e:
        error_type = e.errors()[0]["type"]
        if error_type.index("missing") == 0:
            return response_error_handler({"status": 404})
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


@router.get(
    "/genome/{genome_uuid}/dataset/{dataset_type}/attributes", name="dataset_attributes"
)
async def get_genome_dataset_attributes(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_uuid: str,
    dataset_type: str,
    attribute_names: Annotated[list[str] | None, Query()] = None,
):
    try:
        dataset_attributes = get_dataset_attributes(
            adaptor, genome_uuid, dataset_type, attribute_names
        )
        if len(dataset_attributes.get("attributes", [])) == 0:
            return responses.JSONResponse(
                {
                    "message": f"Could not find details for genome {genome_uuid} and dataset {dataset_type}."
                },
                status_code=404,
            )
        dataset_attributes_object = DatasetAttributes(**dataset_attributes)
        response_data = responses.JSONResponse(
            dataset_attributes_object.dict(), status_code=200
        )
        return response_data

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


@router.get("/genomeid")
async def get_genome_by_keyword(
    adaptor: GenomeAdaptorDep, request: Request, assembly_accession_id: str
):
    try:
        genome_response = get_genomes_by_specific_keyword_iterator(
            db_conn=adaptor,
            tolid=None,
            assembly_accession_id=assembly_accession_id,
            assembly_name=None,
            ensembl_name=None,
            common_name=None,
            scientific_name=None,
            scientific_parlance_name=None,
            species_taxonomy_id=None,
            release_version=None,
        )
        latest_genome_by_keyword_object = GenomeByKeyword()
        for arr in genome_response:
            genome_by_keyword_object = GenomeByKeyword(**arr)
            if (
                genome_by_keyword_object.release_version
                > latest_genome_by_keyword_object.release_version
            ):
                latest_genome_by_keyword_object = genome_by_keyword_object
        if latest_genome_by_keyword_object.genome_uuid:
            return responses.JSONResponse(latest_genome_by_keyword_object.model_dump())
        else:
            logging.error(f"Assembly accession id {assembly_accession_id} not found")
            return response_error_handler({"status": 404})

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_uuid}/vep/file_paths")
async def get_vep_file_paths(
    adaptor: VepAdaptorDep,
    request: Request,
    genome_uuid: str,
):
    try:
        vep_file_paths = get_vep_paths_by_uuid(adaptor, genome_uuid)
        if len(vep_file_paths) == 0:
            return responses.JSONResponse(
                {"message": f"Could not find VEP file paths for genome {genome_uuid}."},
                status_code=404,
            )

        vep_file_paths_object = VepFilePaths(**vep_file_paths)
        return responses.JSONResponse(vep_file_paths_object.dict(), status_code=200)

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


@router.get("/releases", name="get_releases")
@redis_cache("releases")
async def get_releases(
    adaptor: ReleaseAdaptorDep,
    request: Request,
    release_name: list[str] = Query(None, description="Filter by release name(s)"),
    current_only: bool = Query(False, description="Only current releases"),
):
    try:
        releases_stream = release_iterator(
            adaptor,
            site_name=None,
            release_label=release_name,
            current_only=current_only,
        )

        releases_list = []
        for release_msg in releases_stream:
            release = Release(**release_msg)
            releases_list.append(release)

        if releases_list:
            # Serialize each release into the desired format
            response_list = []
            for release in releases_list:
                response_dict = release.model_dump(
                    include={
                        "name": True,
                        "type": True,
                        "is_current": True,
                    }
                )
                response_list.append(response_dict)
            response_data = responses.JSONResponse(response_list, status_code=200)
        else:
            return response_error_handler(
                {"status": 404, "details": "No releases found matching criteria"}
            )
    except Exception as e:
        logging.error(e)
        error_response = {"message": f"An error occurred: {str(e)}"}
        response_data = responses.JSONResponse(error_response, status_code=500)

    return response_data


@router.get("/genome_groups", name="genome_groups")
@redis_cache("genome_groups", arg_keys=["group_type", "release"])
async def get_genome_groups(
    adaptor: GenomeAdaptorDep,
    group_type: str = Query(..., description="Group type, e.g. 'structural_variant'"),
    release: str | None = Query(
        None, description="Optional release label, e.g. '2025-02'"
    ),
):
    try:
        genome_groups_dict = get_genome_groups_by_reference(
            adaptor, group_type, release
        )
        logging.debug(f"genome_groups_dict: {genome_groups_dict}")
        if len(genome_groups_dict.get("genome_groups", [])) == 0:
            return response_error_handler(
                {"status": 404, "details": "No genome groups found matching criteria"}
            )

        genome_groups = GenomeGroupsResponse(**genome_groups_dict)
        response_dict = genome_groups.model_dump()
        return responses.JSONResponse(response_dict, status_code=200)
    except Exception as ex:
        logging.exception("Error in get_genome_groups")
        return response_error_handler({"status": 500})


@router.get("/genome_groups/{group_id}/genomes", name="genomes_in_group")
@redis_cache("genomes_in_group", arg_keys=["group_id", "release"])
async def get_genomes_in_group(
    adaptor: GenomeAdaptorDep,
    group_id: str = Path(..., description="Group ID, e.g. 'grch38-group'"),
    release: str | None = Query(
        None, description="Optional release label, e.g. '2025-02'"
    ),
):
    try:
        genomes_in_group_dict = data_get_genomes_in_group(adaptor, group_id, release)
        logging.debug(f"genomes_in_group_dict: {genomes_in_group_dict}")
        if len(genomes_in_group_dict.get("genomes", [])) == 0:
            return response_error_handler(
                {"status": 404, "details": "No genomes found in specified group"}
            )

        genomes_in_group = GenomesInGroupResponse(**genomes_in_group_dict)
        response_dict = genomes_in_group.model_dump()
        return responses.JSONResponse(response_dict, status_code=200)
    except Exception as ex:
        logging.exception("Error in get_genomes_in_group")
        return response_error_handler({"status": 500})


@router.get("/genome_counts", name="genome_counts")
@redis_cache(key_prefix="genome_counts", arg_keys=["release"])
async def get_genome_counts(
    adaptor: GenomeAdaptorDep,
    release: str | None = Query(
        None, description="Optional release label to filter counts, e.g. '2025-02'"
    ),
):
    try:
        genome_counts_dict = data_get_genome_counts(adaptor, release)
        genome_counts = GenomeCountsResponse(**genome_counts_dict)
        response_data = responses.JSONResponse(
            genome_counts.model_dump(), status_code=200
        )
    except Exception as ex:
        logging.exception("Error in get_genome_counts")
        return response_error_handler({"status": 500})
    return response_data
