"""
See the NOTICE file distributed with this work for additional information
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

import logging
import sys

from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

from .logging import InterceptHandler

VERSION = "0.0.0"
API_PREFIX = "/api"

config = Config(".env")
DEBUG: bool = config("DEBUG", cast=bool, default=False)
PROJECT_NAME: str = config("PROJECT_NAME", default="Ensembl Web Metadata API")
ALLOWED_HOSTS: list[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="*",
)

# GRPC Info
GRPC_HOST: str = config("GRPC_HOST", default="localhost")
GRPC_PORT: int = config("GRPC_PORT", default=50051)

# Caching Config
REDIS_HOST: str = config("REDIS_HOST", default="redis")
REDIS_PORT: int = config("REDIS_PORT", default=6379)
ENABLE_REDIS_CACHE: bool = config("ENABLE_REDIS_CACHE", cast=bool, default=True)
REDIS_MAX_CONNECTION: int = config("REDIS_MAX_CONNECTION", default=10)

# IDENTIFIERS_ORG URL
IDENTIFIERS_ORG_BASE_URL: str = config(
    "IDENTIFIERS_ORG_BASE_URL", default="https://identifiers.org/"
)

ASSEMBLY_URLS = {}

ASSEMBLY_URLS["GCA"] = IDENTIFIERS_ORG_BASE_URL + "insdc.gca/"
ASSEMBLY_URLS["GCF"] = IDENTIFIERS_ORG_BASE_URL + "refseq.gcf/"

# Base URL for FTP download links
FTP_BASE_URL: str = config(
    "FTP_BASE_URL", default="https://ftp.ebi.ac.uk/pub/ensemblorganisms/"
)

# logging configuration
logging.basicConfig(level=logging.DEBUG)
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "uvicorn.access")

log = logging.getLogger("gunicorn.access")

logging.getLogger().handlers = [InterceptHandler()]
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
