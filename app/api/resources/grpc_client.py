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
from ensembl.production.metadata import ensembl_metadata_pb2
from ensembl.production.metadata import ensembl_metadata_pb2_grpc
 
 
# Create Channel
channel = grpc.insecure_channel('{}:{}'.format("localhost", 50051), options=(('grpc.enable_http_proxy', 0),))
 
# Create Stub 
stub = ensembl_metadata_pb2_grpc.EnsemblMetadataStub(channel)

class GRPCClient:
	def __init__(self, host:str, port:int):
		self.host = host
		self.port = port
		# Create Channel
		self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.port), options=(('grpc.enable_http_proxy', 0),))
 
		# Create Stub 
		self.stub = ensembl_metadata_pb2_grpc.EnsemblMetadataStub(channel)

	def get_statistics(genome_id:str):
		return {}

	def get_genome(self, genome_uuid:str):
		# Create request
		request = ensembl_metadata_pb2.GenomeUUIDRequest(genome_uuid=genome_uuid, release_version=None)
 
		# Get response
		response = self.stub.GetGenomeByUUID(request)

		return response

