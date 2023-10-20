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
from app.api.resources.grpc_client import GRPCClient
from google.protobuf.json_format import MessageToDict, MessageToJson
from app.core.config import GRPC_HOST, GRPC_PORT
from app.api.models.statistics import ExampleObjects, GenomeStatistics

genome_uuid = "a7335667-93e7-11ec-a39d-005056b38ce3"
print("connecting to gRPC server on ", GRPC_HOST, ":", GRPC_PORT)
gc = GRPCClient(GRPC_HOST, GRPC_PORT)

genome_info = gc.get_genome(genome_uuid)
genome_as_json = MessageToJson(genome_info)
print(genome_as_json)

top_level_stats = gc.get_statistics(genome_uuid)
top_level_stats_dict = MessageToDict(top_level_stats)
print(top_level_stats_dict)

karyotype_data = gc.get_karyotype(genome_uuid)
print (karyotype_data)


genome_stats = GenomeStatistics(_raw_data=top_level_stats_dict["statistics"])
print ("Example Objects")
print (genome_stats.model_dump(include={"example_objects": True})["example_objects"])

print ("Top Level Stats")
print (genome_stats.model_dump(exclude={"example_objects": True}))
