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
from aiohttp import ClientResponseError

from api.error_response import response_error_handler
from api.models.statistics import GenomeStatistics
from core.config import GRPC_HOST, GRPC_PORT
from core.logging import InterceptHandler

from api.resources.grpc_client import GRPCClient
from google.protobuf.json_format import MessageToDict, MessageToJson
from fastapi.responses import ORJSONResponse

logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()

logger.log("INFO", "Connecting to gRPC server on " + GRPC_HOST + ":" + GRPC_PORT)
grpc_client = GRPCClient(GRPC_HOST, GRPC_PORT)


@router.get(
    "/genome/{genome_uuid}/stats", name="statistics", response_class=ORJSONResponse
)
async def get_metadata_statistics(request: Request, genome_uuid: str):
    try:
        top_level_stats_dict = MessageToDict(grpc_client.get_statistics(genome_uuid))
        compiled_data = {stats_item["name"]: stats_item["statisticValue"] for stats_item in
                         top_level_stats_dict["statistics"]}

        genome_stats = GenomeStatistics(coding_stats=compiled_data)
        return responses.Response(genome_stats.json())
    except (ClientResponseError, Exception) as e:
        logger.log("INFO", e)
        return response_error_handler({"ERROR": e})
