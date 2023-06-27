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
from api.resources.grpc_client import GRPCClient
from google.protobuf.json_format import MessageToDict, MessageToJson
from core.config import GRPC_HOST, GRPC_PORT

print("connecting to gRPC server on ", GRPC_HOST, ":", GRPC_PORT)
gc = GRPCClient(GRPC_HOST, GRPC_PORT)

genome_info = gc.get_genome("a7335667-93e7-11ec-a39d-005056b38ce3")
genome_as_json = MessageToJson(genome_info)
print(genome_as_json)

top_level_stats = gc.get_statistics("a7335667-93e7-11ec-a39d-005056b38ce3")
top_level_stats_dict = MessageToDict(top_level_stats)
print(top_level_stats_dict)
