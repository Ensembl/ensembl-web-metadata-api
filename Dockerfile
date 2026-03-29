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

FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Maintainer
LABEL org.opencontainers.image.authors="ensembl-webteam@ebi.ac.uk"

# we need git because we have dependencies ensembl-metadata-api and ensembl-py
# fix: Git executable not found. Ensure that Git is installed and available.
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \

# Set Work Directory
WORKDIR /app

# Copy source code
COPY . /app/

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked

# Expose Ports
ENV PORT 8014
EXPOSE 8014

RUN mkdir /data

# Run uvicorn server
ENV PYTHONPATH=/app/src
ENV DB_URL=duckdb:////data/duck_meta.db
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8014", "--reload"]

# Run the container like this:
# sudo podman run --mount type=bind,src=data,dst=/data/ -p 8014:8014 container_id
# Expects the DB in ./data/duck_meta.db, will be mounted to /data/duck_meta.db
# in the container
