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

import logging
import grpc
from google.protobuf.json_format import MessageToDict
from grpc_health.v1 import health_pb2_grpc, health_pb2
from yagrc import reflector as yagrc_reflector

logger = logging.getLogger(__name__)

class GRPCClient:
    def __init__(self, host: str, port: int):
        self.grpc_server_address = f"{host}:{port}"
        # Create Channel
        self.channel = grpc.insecure_channel(
            self.grpc_server_address,
            options=(("grpc.enable_http_proxy", 0),),
        )
        self.health_stub = health_pb2_grpc.HealthStub(self.channel)

        self.stub = None  # Default stub (will be set only if gRPC is available)
        self.reflector = yagrc_reflector.GrpcReflectionClient()

        try:
            # Attempt to load gRPC reflection protocols
            self.reflector.load_protocols(
                self.channel, symbols=["ensembl_metadata.EnsemblMetadata"]
            )
            stub_class = self.reflector.service_stub_class("ensembl_metadata.EnsemblMetadata")
            self.stub = stub_class(self.channel)  # Assign stub only if reflection succeeds
            logger.info("gRPC reflection loaded successfully.")
        except grpc.RpcError as e:
            logger.warning(f"Failed to connect to gRPC service at {self.grpc_server_address}. "
                           f"Reflection unavailable. Error: {e.details()}")


    def get_grpc_status(self, service_name: str = ""):
        """
        Checks the health of the gRPC server or a specific service.

        Parameters:
            service_name (str): Name of the gRPC service to check. Empty string `""` checks the entire server.

        Returns:
            dict: {"status": "SERVING" or "NOT_SERVING", "code": "<gRPC Code>"}
        """
        request = health_pb2.HealthCheckRequest(service=service_name)
        try:
            response = self.health_stub.Check(request)
            return {"status": response.status, "code": "OK"}
        except grpc.RpcError as e:
            return {"status": 0, "code": str(e.code().name)}  # Handle errors gracefully


    def get_statistics(self, genome_uuid: str):
        """Returns gRPC message containing statistics for given genome_uuid.

        Parameters
        ----------
        genome_uuid : str, required
                The genome_uuid of the genome
        """
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeUUIDRequest"
        )
        genome_request = request_class(genome_uuid=genome_uuid, release_version=None)
        toplevel_stats_by_uuid = self.stub.GetTopLevelStatisticsByUUID(genome_request)
        return toplevel_stats_by_uuid

    def get_genome_details(self, genome_uuid: str):
        # Create request
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeUUIDRequest"
        )
        request = request_class(genome_uuid=genome_uuid)

        # Get response
        response = self.stub.GetGenomeByUUID(request)

        return response

    def get_brief_genome_details(self, genome_uuid_or_slug: str):
        # Create request
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeUUIDRequest"
        )
        request = request_class(genome_uuid=genome_uuid_or_slug)

        # Get response
        response = self.stub.GetBriefGenomeDetailsByUUID(request)

        return response

    def get_attributes_info(self, genome_uuid: str):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeUUIDRequest"
        )
        request = request_class(genome_uuid=genome_uuid)

        response = self.stub.GetAttributesByGenomeUUID(request)

        return response

    def get_popular_species(self):
        request_class = self.reflector.message_class(
            "ensembl_metadata.OrganismsGroupRequest"
        )
        popular_species = self.stub.GetOrganismsGroupCount(request_class())

        return popular_species

    def get_top_level_regions(self, genome_uuid: str):
        request_class = self.reflector.message_class(
            "ensembl_metadata.AssemblyRegionRequest"
        )
        genome_assembly_request = request_class(
            genome_uuid=genome_uuid, chromosomal_only=True
        )
        top_level_regions = self.stub.GetAssemblyRegion(genome_assembly_request)
        genome_top_level_regions = []
        for tlr in top_level_regions:
            genome_top_level_regions.append(MessageToDict(tlr))
        # Sort region by reank
        genome_top_level_regions.sort(key=lambda region: region["rank"])
        return genome_top_level_regions

    def get_region(self, genome_uuid: str, region_name: str):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeAssemblySequenceRegionRequest"
        )
        genome_seq_region_request = request_class(
            genome_uuid=genome_uuid, sequence_region_name=region_name
        )
        genome_seq_region = self.stub.GetGenomeAssemblySequenceRegion(
            genome_seq_region_request
        )
        return genome_seq_region

    def get_ftplinks(self, genome_uuid: str):
        request_class = self.reflector.message_class("ensembl_metadata.FTPLinksRequest")
        ftp_links_request = request_class(genome_uuid=genome_uuid, dataset_type="all")
        return self.stub.GetFTPLinks(ftp_links_request)

    def get_region_checksum(self, genome_uuid: str, region_name: str):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeAssemblySequenceRegionRequest"
        )
        region_checksum = request_class(
            genome_uuid=genome_uuid, sequence_region_name=region_name
        )
        return self.stub.GetGenomeAssemblySequenceRegion(region_checksum)

    def get_dataset_attributes(
        self, genome_uuid: str, dataset_type: str, attribute_names: list
    ):
        request_class = self.reflector.message_class(
            "ensembl_metadata.DatasetAttributesValuesRequest"
        )
        if attribute_names:
            dataset_attributes = request_class(
                genome_uuid=genome_uuid,
                dataset_type=dataset_type,
                attribute_name=attribute_names,
            )
        else:
            dataset_attributes = request_class(
                genome_uuid=genome_uuid, dataset_type=dataset_type
            )
        return self.stub.GetAttributesValuesByUUID(dataset_attributes)

    def get_genome_by_specific_keyword(self, **kwargs):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeBySpecificKeywordRequest"
        )
        request = request_class(**kwargs)
        response = self.stub.GetGenomesBySpecificKeyword(request)
        return response

    def get_vep_file_paths(self, genome_uuid: str):
        request_class = self.reflector.message_class("ensembl_metadata.GenomeUUIDOnlyRequest")
        vep_file_paths_request = request_class(genome_uuid=genome_uuid)
        return self.stub.GetVepFilePathsByUUID(vep_file_paths_request)
