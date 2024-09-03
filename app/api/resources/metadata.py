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
import logging

from fastapi import APIRouter, Request, responses
from loguru import logger
from pydantic import ValidationError

from api.error_response import response_error_handler
from api.models.checksums import Checksum
from api.models.statistics import GenomeStatistics, ExampleObjectList
from api.models.popular_species import PopularSpeciesGroup
from api.models.karyotype import Karyotype
from api.models.genome import GenomeDetails, DatasetAttributes
from api.models.ftplinks import FTPLinks

from core.config import GRPC_HOST, GRPC_PORT
from core.logging import InterceptHandler

from api.resources.grpc_client import GRPCClient
from api.models.region_validation import RegionValidation

from google.protobuf.json_format import MessageToDict

logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()

logger.info("Connecting to gRPC server on " + GRPC_HOST + ":" + str(GRPC_PORT))
grpc_client = GRPCClient(GRPC_HOST, GRPC_PORT)


@router.get("/genome/{genome_uuid}/stats", name="statistics")
async def get_metadata_statistics(request: Request, genome_uuid: str):
    try:
        top_level_stats_dict = MessageToDict(grpc_client.get_statistics(genome_uuid))
        genome_stats = GenomeStatistics(_raw_data=top_level_stats_dict["statistics"])
        return responses.JSONResponse({"genome_stats": genome_stats.model_dump()})
    except Exception as e:
        logger.exception(e)
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
        logger.debug(e)
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
        logger.debug(e)
        return response_error_handler({"status": 500})


@router.get("/validate_location", name="validate_location")
def validate_region(request: Request, genome_id: str, location: str):
    try:
        rgv = RegionValidation(genome_uuid=genome_id, location_input=location)
        rgv.validate_region()
        return responses.JSONResponse(rgv.model_dump())
    except Exception as e:
        logger.debug(e)
        return response_error_handler({"status": 500})


@router.get("/genome/{genome_id}/example_objects", name="example_objects")
def example_objects(request: Request, genome_id: str):
    try:
        genome_details_dict = MessageToDict(grpc_client.get_genome_details(genome_id))
        if genome_details_dict:
            example_objects = ExampleObjectList(
                example_objects=genome_details_dict["attributesInfo"]
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
        logger.debug(ex)
        return response_error_handler({"status": 500})
    return response_data


@router.get("/genome/{genome_uuid}/details", name="genome_details")
async def get_genome_details(request: Request, genome_uuid: str):
    try:
        genome_details_dict = MessageToDict(grpc_client.get_genome_details(genome_uuid))
        if genome_details_dict:
            genome_details = GenomeDetails(**genome_details_dict)
            response_data = responses.JSONResponse(genome_details.model_dump())
        else:
            not_found_response = {
                "message": "Could not find details for {}".format(genome_uuid)
            }
            response_data = responses.JSONResponse(not_found_response, status_code=404)
    except Exception as ex:
        logger.debug(ex)
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
        logger.debug(ex)
        return response_error_handler({"status": 500})


@router.get("/genome/{slug}/explain", name="genome_explain")
async def explain_genome(request: Request, slug: str):
    not_found_response = {"message": "Could not explain {}".format(slug)}
    response_data = responses.JSONResponse(not_found_response, status_code=404)
    try:
        genome_uuid = grpc_client.get_genome_uuid_from_tag(slug)
        if not genome_uuid:
            genome_uuid = slug
        genome_details_dict = MessageToDict(grpc_client.get_genome_details(genome_uuid))
        if genome_details_dict:
            genome_details = GenomeDetails(**genome_details_dict)
            response_dict = genome_details.model_dump(
                include={
                    "genome_id": True,
                    "genome_tag": True,
                    "scientific_name": True,
                    "species_taxonomy_id": True,
                    "common_name": True,
                    "is_reference": True,
                    "assembly": {"name", "accession_id"},
                    "type": True,
                }
            )
            response_data = responses.JSONResponse(response_dict, status_code=200)
    except Exception as ex:
        logger.debug(ex)
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
        logger.debug(ex)
        return response_error_handler({"status": 500})


@router.get(
    "/genome/{genome_uuid}/dataset/{dataset_type}/attributes", name="dataset_attributes"
)
async def get_genome_dataset_attributes(
    request: Request, genome_uuid: str, dataset_type: str
):
    try:
        dataset_attributes = MessageToDict(
            grpc_client.get_dataset_attributes(
                genome_uuid=genome_uuid, dataset_type=dataset_type
            )
        )
        if dataset_attributes == {}:
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
        logger.debug(ex)
        return response_error_handler({"status": 500})
