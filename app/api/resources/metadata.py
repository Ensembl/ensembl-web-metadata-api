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

GRPC_HOST = os.getenv("GRPC_HOST", "localhost")
GRPC_PORT = os.getenv("GRPC_PORT", 50051)

print("Connecting to gRPC server on ", GRPC_HOST, ":", GRPC_PORT)
gc = GRPCClient(GRPC_HOST, GRPC_PORT)

# Is class name sensible here ?
# Or this should also say top_level_statistics
class GenomeStatistics:
    def __init__(self, raw_data: dict):
        self.raw_stats = raw_data
        # Extrack name, staticValue from the raw statistics
        self.rearranged_stats = {
            stats_item["name"]: int(float(stats_item["statisticValue"]))
            for stats_item in self.raw_stats
        }

    def prepare_assembly_stats(self):
        try:
            assembly_stats = {
                "contig_n50": self.rearranged_stats.get("contig_n50", None),
                "total_genome_length": self.rearranged_stats.get(
                    "total_genome_length", None
                ),
                "total_coding_sequence_length": self.rearranged_stats.get(
                    "total_coding_sequence_length", None
                ),
                "total_gap_length": self.rearranged_stats.get("total_gap_length", None),
                "spanned_gaps": self.rearranged_stats.get("spanned_gaps", None),
                "chromosomes": self.rearranged_stats.get("chromosomes", None),
                "toplevel_sequences": self.rearranged_stats.get(
                    "toplevel_sequences", None
                ),
                "component_sequences": self.rearranged_stats.get(
                    "component_sequences", None
                ),
                "gc_percentage": self.rearranged_stats.get("gc_percentage", None),
            }
            return assembly_stats
        except Exception as e:
            logger.log("DEBUG", e)

    def prepare_variation_stats(self):
        try:
            variation_stats = {
                "short_variants": self.rearranged_stats.get("short_variants", None),
                "structural_variants": self.rearranged_stats.get(
                    "structural_variants", None
                ),
                "short_variants_with_phenotype_assertions": self.rearranged_stats.get(
                    "short_variants_with_phenotype_assertions", None
                ),
                "short_variants_with_publications": self.rearranged_stats.get(
                    "short_variants_with_publications", None
                ),
                "short_variants_frequency_studies": self.rearranged_stats.get(
                    "short_variants_frequency_studies", None
                ),
                "structural_variants_with_phenotype_assertions": self.rearranged_stats.get(
                    "structural_variants_with_phenotype_assertions", None
                ),
            }
            return variation_stats
        except Exception as e:
            logger.log("DEBUG", e)

    def prepare_stats(self):
        try:
            genome_stats = {
                "genome_stats": {
                    "assembly_stats": self.prepare_assembly_stats(),
                    "variation_stats": self.prepare_variation_stats(),
                }
            }
            return genome_stats
        except Exception as e:
            logger.log("DEBUG", e)


@router.get(
    "/genome/{genome_uuid}/stats", name="statistics", response_class=ORJSONResponse
)
async def get_metadata_statistics(request: Request, genome_uuid: str):
    try:
        top_level_stats = gc.get_statistics(genome_uuid)
        top_level_stats_dict = MessageToDict(top_level_stats)
        gs = GenomeStatistics(top_level_stats_dict["statistics"])
        genome_stats = gs.prepare_stats()
        return ORJSONResponse(genome_stats)
    except (ClientResponseError, Exception) as e:
        logger.log("DEBUG", e)
        return response_error_handler({"EROR": e})
