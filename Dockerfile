#
#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

FROM python:3.11

LABEL org.opencontainers.image.authors="ensembl-webteam@ebi.ac.uk"

WORKDIR /app

# Copy source code
COPY ./src /app/
COPY ./scripts /app/
COPY requirements.txt requirements.txt
# Install dependencies
RUN pip install  -r requirements.txt

# Expose Ports
ENV PORT 8014
EXPOSE 8014

RUN mkdir /data

# Run uvicorn server
ENV PYTHONPATH=/app/
ENV DB_URL=duckdb:////data/duck_meta.db
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8014", "--reload"]

# Run the container like this:
# sudo podman run --mount type=bind,src=data,dst=/data/ -p 8014:8014 container_id
# Expects the DB in ./data/duck_meta.db, will be mounted to /data/duck_meta.db
# in the container
