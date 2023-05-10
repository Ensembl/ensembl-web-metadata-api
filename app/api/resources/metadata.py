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

from aiohttp import ClientResponseError
from fastapi import APIRouter, Request, responses
from loguru import logger

from api.error_response import response_error_handler
from core.logging import InterceptHandler
import json

logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()


@router.get("/statistics", name="statistics")
async def get_metadata_statistics(request: Request):
    """"""
    sample_response = {
        "assembly_name": "GRCh38.p13",
        "common_name": "Human",
        "genome_id": "a7335667-93e7-11ec-a39d-005056b38ce3",
        "genome_tag": "grch38",
        "image": "https://beta.ensembl.org/static/genome_images/homo_sapiens_38.svg",
        "is_available": True,
        "popular_order": 0,
        "reference_genome_id": None,
        "scientific_name": "Homo sapiens",
    }
    try:
        return responses.Response(content=json.dumps(sample_response))

    except (ClientResponseError, Exception) as e:
        logger.log("DEBUG", e)
        return response_error_handler({"EROR": e})
