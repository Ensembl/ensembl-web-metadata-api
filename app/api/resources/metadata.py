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
from core.logging import InterceptHandler
import json
import os
from api.resources.grpc_client import GRPCClient 
from google.protobuf.json_format import MessageToDict, MessageToJson
from fastapi.responses import ORJSONResponse


logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()

GRPC_HOST=os.getenv('GRPC_HOST','localhost')
GRPC_PORT=os.getenv('GRPC_PORT',50051)

print ("connecting to gRPC server on ", GRPC_HOST, ":", GRPC_PORT)
gc = GRPCClient(GRPC_HOST, GRPC_PORT)

# Is class name sensible here ? 
# Or this should also say top_level_statistics
class GenomeStatistics:
    def __init__(self, raw_data:dict):
        self.raw_stats = raw_data
        # Extrack name, staticValue from the raw statistics
        self.rearranged_stats = { stats_item['name']:int(float(stats_item['statisticValue'])) for stats_item in self.raw_stats }


@router.get("/genome/{genome_uuid}/stats", name="statistics", response_class=ORJSONResponse)
async def get_metadata_statistics(request: Request, genome_uuid:str):
    try:
        top_level_stats = gc.get_statistics(genome_uuid)
        return ORJSONResponse(MessageToDict(top_level_stats))
    except (ClientResponseError, Exception) as e:
        logger.log("DEBUG", e)
        return response_error_handler({"EROR": e})
