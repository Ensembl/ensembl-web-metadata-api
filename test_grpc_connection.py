from app.api.resources.grpc_client import GRPCClient



gc = GRPCClient('localhost', 50051)

genome_info = gc.get_genome("a7335667-93e7-11ec-a39d-005056b38ce3")

print (genome_info)