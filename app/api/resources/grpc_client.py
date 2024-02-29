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
from google.protobuf.json_format import MessageToDict
from yagrc import reflector as yagrc_reflector

from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

grpc_client_instrumentor = GrpcInstrumentorClient()
grpc_client_instrumentor.instrument()

class GRPCClient:

    def __init__(self, host: str, port: int):
        # Create Channel
        channel = grpc.insecure_channel(
            "{}:{}".format(host, port),
            options=(("grpc.enable_http_proxy", 0),),
        )
        self.reflector = yagrc_reflector.GrpcReflectionClient()
        self.reflector.load_protocols(channel, symbols=["ensembl_metadata.EnsemblMetadata"])
        stub_class = self.reflector.service_stub_class("ensembl_metadata.EnsemblMetadata")
        self.stub = stub_class(channel)

    def get_statistics(self, genome_uuid: str):
        """Returns gRPC message containing statistics for given genome_uuid.

        Parameters
        ----------
        genome_uuid : str, required
                The genome_uuid of the genome
        """
        request_class = self.reflector.message_class("ensembl_metadata.GenomeUUIDRequest")
        genome_request = request_class(
            genome_uuid=genome_uuid, release_version=None
        )
        toplevel_stats_by_uuid = self.stub.GetTopLevelStatisticsByUUID(genome_request)
        return toplevel_stats_by_uuid

    def get_genome_details(self, genome_uuid: str):
        # Create request
        request_class = self.reflector.message_class("ensembl_metadata.GenomeUUIDRequest")
        request = request_class(genome_uuid=genome_uuid)

        # Get response
        response = self.stub.GetGenomeByUUID(request)

        return response

    def get_popular_species(self):
        request_class = self.reflector.message_class("ensembl_metadata.OrganismsGroupRequest")
        popular_species = self.stub.GetOrganismsGroupCount(request_class())

        return popular_species

    def get_top_level_regions(self, genome_uuid: str):
        request_class = self.reflector.message_class("ensembl_metadata.AssemblyRegionRequest")
        genome_assembly_request = request_class(
            genome_uuid=genome_uuid,
            chromosomal_only=True
        )
        top_level_regions = self.stub.GetAssemblyRegion(genome_assembly_request)
        genome_top_level_regions = []
        for tlr in top_level_regions:
            genome_top_level_regions.append(MessageToDict(tlr))
        # Sort region by reank
        genome_top_level_regions.sort(key=lambda region: region["rank"])
        return genome_top_level_regions

    def get_region(self, genome_uuid: str, region_name: str):
        request_class = self.reflector.message_class("ensembl_metadata.GenomeAssemblySequenceRegionRequest")
        genome_seq_region_request = request_class(
            genome_uuid=genome_uuid,
            sequence_region_name=region_name
        )
        genome_seq_region = self.stub.GetGenomeAssemblySequenceRegion(genome_seq_region_request)
        return genome_seq_region

    def get_genome_uuid_from_tag(self, tag):
        request_class = self.reflector.message_class("ensembl_metadata.GenomeTagRequest")
        uuid_request = request_class(genome_tag=tag)
        genome_uuid_data = self.stub.GetGenomeUUIDByTag(uuid_request)
        if genome_uuid_data.genome_uuid:
            return genome_uuid_data.genome_uuid
        return None

    def get_ftplinks(self, genome_uuid: str):
        request_class = self.reflector.message_class("ensembl_metadata.FTPLinksRequest")
        ftp_links_request = request_class(genome_uuid=genome_uuid, dataset_type="all")
        return self.stub.GetFTPLinks(ftp_links_request)

    def get_region_checksum(self, genome_uuid: str, region_name: str):
        request_class = self.reflector.message_class("ensembl_metadata.GenomeAssemblySequenceRegionRequest")
        region_checksum = request_class(genome_uuid=genome_uuid, sequence_region_name=region_name)
        return self.stub.GetGenomeAssemblySequenceRegion(region_checksum)
