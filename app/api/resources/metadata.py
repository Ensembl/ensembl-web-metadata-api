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

from fastapi import APIRouter, Request, responses
from loguru import logger

from api.error_response import response_error_handler
from api.models.statistics import GenomeStatistics
from api.models.popular_species import PopularSpeciesGroup
from api.models.karyotype import Karyotypes
from core.config import GRPC_HOST, GRPC_PORT
from core.logging import InterceptHandler

from api.resources.grpc_client import GRPCClient
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
        return responses.JSONResponse({"genome_stats": genome_stats.dict()})
    except Exception as e:
        return response_error_handler({"status": 500})

@router.get("/genome/{genome_uuid}/karyotype", name="karyotype")
async def get_genome_karyotype(request: Request, genome_uuid: str):
    try:
        karyotypes = grpc_client.get_karyotype(genome_uuid)
        karyotype_response = Karyotypes(karyotypes=karyotypes)
        return responses.JSONResponse(karyotype_response.dict()["karyotypes"])
    except Exception as e:
        logger.debug(e)
        return response_error_handler({"status": 500})

@router.get("/popular_species", name="popular_species")
async def get_popular_species(request: Request):
    try:
        popular_species_dict = MessageToDict(grpc_client.get_popular_species())
        popular_species = popular_species_dict['organismsGroupCount']
        popular_species_response = PopularSpeciesGroup(_base_url=request.base_url, popular_species=popular_species)
        return responses.JSONResponse(popular_species_response.dict())
    except Exception as e:
        logger.debug(e)
        return response_error_handler({"status": 500})
