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
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Request, responses, Query
from pydantic import ValidationError

from api.error_response import response_error_handler
from api.models.checksums import Checksum
from api.models.statistics import GenomeStatistics, ExampleObjectList
from api.models.popular_species import PopularSpeciesGroup
from api.models.karyotype import Karyotype
from api.models.genome import BriefGenomeDetails, GenomeDetails, DatasetAttributes, GenomeByKeyword, Release
from api.models.ftplinks import FTPLinks
from api.models.vep import VepFilePaths

from core.config import GRPC_HOST, GRPC_PORT
from core.logging import InterceptHandler

from api.resources.grpc_client import GRPCClient
from api.models.region_validation import RegionValidation

from google.protobuf.json_format import MessageToDict

logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()

logging.info("Connecting to gRPC server on " + GRPC_HOST + ":" + str(GRPC_PORT))
grpc_client = GRPCClient(GRPC_HOST, GRPC_PORT)


@router.get("/genome/{genome_uuid}/stats", name="statistics")
async def get_metadata_statistics(request: Request, genome_uuid: str):
    try:
        top_level_stats_dict = MessageToDict(grpc_client.get_statistics(genome_uuid))
        genome_stats = GenomeStatistics(_raw_data=top_level_stats_dict["statistics"])
        return responses.JSONResponse({"genome_stats": genome_stats.model_dump()})
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_uuid}/karyotype", name="karyotype")
async def get_genome_karyotype(request: Request, genome_uuid: str):
    try:
        top_level_regions = grpc_client.get_top_level_regions(genome_uuid)

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
async def get_popular_species(request: Request):
    try:
        popular_species_dict = MessageToDict(grpc_client.get_popular_species())
        popular_species = popular_species_dict["organismsGroupCount"]
        popular_species_response = PopularSpeciesGroup(
            _base_url=request.headers["host"], popular_species=popular_species
        )
        return responses.JSONResponse(popular_species_response.model_dump())
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


@router.get("/validate_location", name="validate_location")
def validate_region(request: Request, genome_id: str, location: str):
    try:
        rgv = RegionValidation(genome_uuid=genome_id, location_input=location)
        rgv.validate_region()
        return responses.JSONResponse(rgv.model_dump())
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_id}/example_objects", name="example_objects")
def example_objects(request: Request, genome_id: str):
    try:
        attributes_info = MessageToDict(grpc_client.get_attributes_info(genome_id))
        if attributes_info:
            example_objects = ExampleObjectList(
                example_objects=attributes_info["attributesInfo"]
            )
            response_data = responses.JSONResponse(
                example_objects.model_dump()["example_objects"]
            )
        else:
            not_found_response = {
                "message": "Could not find example objects for {}".format(genome_id)
            }
            response_data = responses.JSONResponse(not_found_response, status_code=404)
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


@router.get("/genome/{genome_uuid}/details", name="genome_details")
async def get_genome_details(request: Request, genome_uuid: str):
    try:
        genome_details_dict = MessageToDict(grpc_client.get_genome_details(genome_uuid))
        if genome_details_dict:
            genome_details = GenomeDetails(**genome_details_dict)
            response_data = responses.JSONResponse(genome_details.model_dump(
                exclude={
                    "release": {"is_current"},
                }
            ))
        else:
            not_found_response = {
                "message": "Could not find details for {}".format(genome_uuid)
            }
            response_data = responses.JSONResponse(not_found_response, status_code=404)
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


@router.get("/genome/{genome_uuid}/ftplinks", name="genome_ftplinks")
async def get_genome_ftplinks(request: Request, genome_uuid: str):
    try:
        ftplinks_dict = MessageToDict(grpc_client.get_ftplinks(genome_uuid))

        # This is temporary solution to hide regulation ftp links
        # It should be removed once the ftp links for regulation is fixed
        ftplinks_no_regulation = {}
        ftplinks_no_regulation["Links"] = [
            link
            for link in ftplinks_dict["Links"]
            if link["datasetType"] != "regulation"
        ]

        ftplinks = FTPLinks(**ftplinks_no_regulation)
        return responses.JSONResponse(ftplinks.model_dump().get("links", []))
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_id_or_slug}/explain", name="genome_explain")
async def explain_genome(request: Request, genome_id_or_slug: str):
    not_found_response = {"message": "Could not explain {}".format(genome_id_or_slug)}
    response_data = responses.JSONResponse(not_found_response, status_code=404)
    try:
        genome_details_dict = MessageToDict(grpc_client.get_brief_genome_details(genome_id_or_slug))
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
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


@router.get("/genome/{genome_uuid}/checksum/{region_name}", name="region_checksum")
async def get_genome_ftplinks(request: Request, genome_uuid: str, region_name: str):
    try:
        region_checksum_dict = MessageToDict(
            grpc_client.get_region_checksum(
                genome_uuid=genome_uuid, region_name=region_name
            )
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
    request: Request,
    genome_uuid: str,
    dataset_type: str,
    attribute_names: Annotated[list[str] | None, Query()] = None,
):
    try:
        dataset_attributes = MessageToDict(
            grpc_client.get_dataset_attributes(
                genome_uuid=genome_uuid,
                dataset_type=dataset_type,
                attribute_names=attribute_names,
            )
        )
        if len(dataset_attributes.get("attributes",[])) == 0:
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
async def get_genome_by_keyword(request: Request, assembly_accession_id: str):
    try:
        genome_response = grpc_client.get_genome_by_specific_keyword(assembly_accession_id=assembly_accession_id)
        latest_genome_by_keyword_object = GenomeByKeyword()
        for arr in genome_response:
            arr = MessageToDict(arr)
            genome_by_keyword_object = GenomeByKeyword(**arr)
            if (genome_by_keyword_object.release_version > latest_genome_by_keyword_object.release_version):
                latest_genome_by_keyword_object = genome_by_keyword_object
        if (latest_genome_by_keyword_object.genome_uuid):
            return responses.JSONResponse(latest_genome_by_keyword_object.model_dump())
        else:            
            logging.error(f"Assembly accession id {assembly_accession_id} not found")
            return response_error_handler({"status": 404})

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})

@router.get("/genome/{genome_uuid}/vep/file_paths")
async def get_vep_file_paths(
    request: Request,
    genome_uuid: str,
):
    try:
        vep_file_paths = MessageToDict(
            grpc_client.get_vep_file_paths(genome_uuid=genome_uuid)
        )
        if len(vep_file_paths) == 0:
            return responses.JSONResponse(
                {
                    "message": f"Could not find VEP file paths for genome {genome_uuid}."
                },
                status_code=404,
            )

        vep_file_paths_object = VepFilePaths(**vep_file_paths)
        return responses.JSONResponse(
            vep_file_paths_object.dict(), status_code=200
        )

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


@router.get("/releases", name="get_releases")
async def get_releases(
    request: Request,
    release_name: list[str] = Query(None, description="Filter by release name(s)"),
    current_only: bool = Query(False, description="Only current releases")
):
    try:
        releases_stream = grpc_client.get_release(
            release_label=release_name,
            current_only=current_only
        )

        releases_list = []
        for release_msg in releases_stream:
            release_dict = MessageToDict(release_msg)
            release = Release(**release_dict)
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
            response_data = responses.JSONResponse(
                {"message": "No releases found matching criteria"},
                status_code=404
            )

    except Exception as e:
        logging.error(e)
        error_response = {"message": f"An error occurred: {str(e)}"}
        response_data = responses.JSONResponse(error_response, status_code=500)

    return response_data
