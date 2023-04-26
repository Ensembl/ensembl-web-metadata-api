## gRPC-REST bridge for Ensembl Metadata API

gRPC-REST bridge is a proxy server that serves [Ensembl Metadata API](https://github.com/Ensembl/ensembl-metadata-service) gRPC API as REST API (JSON payloads in POST requests). The server is written in Go and its Ensembl API-specific modules have been generated using [gRPC JSON gateway](https://github.com/grpc-ecosystem/grpc-gateway/tree/main) protoc plugin. The generated server code is written in Go, wihch is compiled to binary executable and acts as a standalone proxy between the client and gRPC service.

### Dependencies

-   [Go](https://go.dev/doc/install)
-   [Ensembl Metadata gRPC service](https://github.com/Ensembl/ensembl-metadata-service)

### Usage

-   Build the proxy server binary: `go build`
-   Run the server: `rest-bridge --endpoint=<ensembl-gRPC-URL>`
    -   Default Ensembl gRPC URL: `localhost:50051` (local Ensembl gRPC service, see the [repo](https://github.com/Ensembl/ensembl-metadata-service) for setup instructions)
-   Run a query: `curl -X POST -k https://localhost:8081/<path> -H "Content-Type: text/plain" -d '{"key": "value"}'`,
    where path and payload values come from the Ensembl Metadata protobuf definitions, e.g. `https://localhost:8081/ensembl_metadata.EnsemblMetadata/GetSpeciesInformation -d '{"genomeUuid": "3704ceb1-948d-11ec-a39d-005056b38ce3"}'`
