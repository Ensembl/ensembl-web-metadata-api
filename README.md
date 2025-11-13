# Ensembl Web Metadata API
Metadata API for new Ensembl website (https://beta.ensembl.org)

### Deploy the app and run docker-compose:
```bash
git clone https://github.com/Ensembl/ensembl-web-metadata-api
cd ensembl-web-metadata-api
vi .env #add values for PORT, GRPC_HOST, GRPC_PORT
docker-compose -f docker-compose.yml up
```

### Run unit tests:
```bash
docker-compose -f docker-compose.yml run metadata_api python -m unittest
```

### Run locally without Docker:
```bash
git clone https://github.com/Ensembl/ensembl-web-metadata-api
cd ensembl-web-metadata-api
pip install -r requirements.txt
PYTHONPATH='app' uvicorn main:app --host 0.0.0.0 --port 8014 --reload
```
 
