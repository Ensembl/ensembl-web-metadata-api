# Ensembl Web Metadata API
Metadata API for new Ensembl website (https://beta.ensembl.org)

### Deploy the app and run docker-compose:
```
$ git clone https://github.com/Ensembl/ensembl-web-metadata-api
$ cd ensembl-web-metadata-api
$ docker-compose -f docker-compose.yml up
```

### Run unit tests:
```
$ docker-compose -f docker-compose.yml run metadata_api python -m unittest
```
 
