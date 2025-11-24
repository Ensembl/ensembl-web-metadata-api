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
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeUUIDRequest"
        )
        request = request_class(genome_uuid=genome_uuid)
        response = self.stub.GetGenomeByUUID(request)
        return response

    def get_brief_genome_details(self, genome_uuid_or_slug: str):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeUUIDRequest"
        )
        request = request_class(genome_uuid=genome_uuid_or_slug)
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

        # Sort the list of regions by two criteria:
        # 1. By "rank" if present, regions without a rank are considered to have the highest possible rank (so they go last)
        # 2. Then by "length", which is stored as a string, so we convert it to an integer for proper numeric sorting
        genome_top_level_regions.sort(
            key=lambda region: (
                # Use the value of "rank" if it exists, otherwise use infinity
                # This ensures regions without a rank are placed at the end of the list
                region.get("rank", float("inf")),

                # Convert the "length" from string to integer so numeric comparison works correctly
                # If "length" is missing, treat it as 0
                int(region.get("length", 0))
            )
        )
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

    def get_release(self, release_label: list[str], current_only: bool):
        request_class = self.reflector.message_class("ensembl_metadata.ReleaseRequest")
        request = request_class(release_label=release_label, current_only=current_only)
        return self.stub.GetRelease(request)

    def get_genome_groups_with_reference(self, group_type: str, release_label: str):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GroupTypeRequest"
        )
        request = request_class(group_type=group_type, release_label=release_label)
        return self.stub.GetGenomeGroupsWithReference(request)

    def get_genomes_in_group(self, group_id: str, release_label: str):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomesInGroupRequest"
        )
        request = request_class(group_id=group_id, release_label=release_label)
        return self.stub.GetGenomesInGroup(request)

    def get_genome_counts(self, release_label: str | None):
        request_class = self.reflector.message_class(
            "ensembl_metadata.GenomeCountsRequest"
        )
        request = request_class(release_label=release_label)
        return self.stub.GetGenomeCounts(request)
