import grpc
from ensembl.production.metadata import ensembl_metadata_pb2
from ensembl.production.metadata import ensembl_metadata_pb2_grpc
 
 
# Create Channel
channel = grpc.insecure_channel('{}:{}'.format("localhost", 50051), options=(('grpc.enable_http_proxy', 0),))
 
# Create Stub 
stub = ensembl_metadata_pb2_grpc.EnsemblMetadataStub(channel)
 
# Create request
request = ensembl_metadata_pb2.GenomeUUIDRequest(genome_uuid="a7335667-93e7-11ec-a39d-005056b38ce3", release_version=None)
 
# Get response
response = stub.GetGenomeByUUID(request)
 
# print data
print (response)