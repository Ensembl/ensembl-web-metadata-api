import grpc
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict

from ensembl.production.metadata.ensembl_metadata_pb2 import \
    GenomeUUIDRequest, GenomeNameRequest, \
    ReleaseRequest, GenomeSequenceRequest, AssemblyIDRequest, GenomeByKeywordRequest, AssemblyAccessionIDRequest, \
    OrganismIDRequest, DatasetsRequest, GenomeDatatypeRequest

import ensembl.production.metadata.ensembl_metadata_pb2_grpc as ensembl_metadata_pb2_grpc


def get_assembly_information(stub):
    request1 = AssemblyIDRequest(assembly_id='2')
    releases1 = stub.GetAssemblyInformation(request1)
    print('**** Assembly information ****')
    print(releases1.sequence_checksum)


def get_top_level_statistics(stub):
    request1 = OrganismIDRequest(organism_id='3')
    releases1 = stub.GetTopLevelStatistics(request1)
    print('**** Top level statistics ****')
    print(len(MessageToDict(releases1)))

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = ensembl_metadata_pb2_grpc.EnsemblMetadataStub(channel)
        get_assembly_information(stub)
        get_top_level_statistics(stub)



if __name__ == '__main__':
    run()
