# Ensembl Web Metadata API
Metadata API for new Ensembl website (https://beta.ensembl.org)

### Deploy the app and run docker-compose:
```bash
git clone https://github.com/Ensembl/ensembl-web-metadata-api
cd ensembl-web-metadata-api
vi .env #add values for PORT, GRPC_HOST, GRPC_PORT
source .env
docker-compose -f docker-compose.yml up
```

### Run unit tests:
```bash
docker-compose -f docker-compose.yml run metadata_api python -m unittest
```
 
