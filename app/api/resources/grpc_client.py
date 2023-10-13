"""
.. See the NOTICE file distributed with this work for additional information
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

import grpc
from ensembl.production.metadata.grpc import ensembl_metadata_pb2
from ensembl.production.metadata.grpc import ensembl_metadata_pb2_grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger

class GRPCClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        # Create Channel
        self.channel = grpc.insecure_channel(
            "{}:{}".format(self.host, self.port),
            options=(("grpc.enable_http_proxy", 0),),
        )

        # Create Stub
        self.stub = ensembl_metadata_pb2_grpc.EnsemblMetadataStub(self.channel)

    def get_statistics(self, genome_uuid: str):
        """Returns gRPC message containing statistics for given genome_uuid.

        Parameters
        ----------
        genome_uuid : str, required
                The genome_uuid of the genome
        """

        genome_request = ensembl_metadata_pb2.GenomeUUIDRequest(
            genome_uuid=genome_uuid, release_version=None
        )
        toplevel_stats_by_uuid = self.stub.GetTopLevelStatisticsByUUID(genome_request)
        return toplevel_stats_by_uuid

    def get_genome(self, genome_uuid: str):
        # Create request
        request = ensembl_metadata_pb2.GenomeUUIDRequest(
            genome_uuid=genome_uuid, release_version=None
        )

        # Get response
        response = self.stub.GetGenomeByUUID(request)

        return response

    def get_popular_species(self):
        popular_species_request = ensembl_metadata_pb2.OrganismsGroupRequest()
        popular_species = self.stub.GetOrganismsGroupCount(popular_species_request)

        return popular_species

    def get_top_level_regions(self, genome_uuid: str):
        genome_assembly_request = ensembl_metadata_pb2.GenomeAssemblySequenceRequest(
            genome_uuid=genome_uuid,
            chromosomal_only=True
            )
        top_level_regions = self.stub.GetGenomeAssemblySequence(genome_assembly_request)
        genome_top_level_regions = []
        for tlr in top_level_regions:
            genome_top_level_regions.append(MessageToDict(tlr))
        return genome_top_level_regions

    def get_region(self, genome_uuid: str, region_name: str):
        genome_seq_region_request = ensembl_metadata_pb2.GenomeAssemblySequenceRegionRequest(
            genome_uuid=genome_uuid,
            sequence_region_name=region_name,
            chromosomal_only=False
        )
        genome_seq_region = self.stub.GetGenomeAssemblySequenceRegion(genome_seq_region_request)
        return genome_seq_region