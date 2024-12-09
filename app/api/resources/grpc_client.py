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
from yagrc import reflector as yagrc_reflector


class GRPCClient:
    def __init__(self, host: str, port: int):
        # Create Channel
        channel = grpc.insecure_channel(
            "{}:{}".format(host, port),
            options=(("grpc.enable_http_proxy", 0),),
        )
        self.reflector = yagrc_reflector.GrpcReflectionClient()
        self.reflector.load_protocols(
            channel, symbols=["ensembl_metadata.EnsemblMetadata"]
        )
        stub_class = self.reflector.service_stub_class(
            "ensembl_metadata.EnsemblMetadata"
        )
        self.stub = stub_class(channel)

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

    def get_genome_by_specific_keyword(self, assembly_accession_id: str):
        # Create request
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeBySpecificKeywordRequest"
        )
        request = request_class(assembly_accession_id=assembly_accession_id)
        response = self.stub.GetGenomesBySpecificKeyword(request)
        return response