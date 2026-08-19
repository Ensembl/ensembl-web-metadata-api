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

import ecs_logging


class _UvicornAccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Add searchable HTTP fields to Uvicorn access logs.
        if record.name != "uvicorn.access":
            return True

        if not isinstance(record.args, tuple):
            return True

        try:
            _, method, _, http_version, status_code = record.args
        except ValueError:
            return True

        if not isinstance(status_code, int):
            return True

        record.__dict__.update(
            {
                "http.request.method": method,
                "http.response.status_code": status_code,
                "http.version": http_version,
            }
        )
        return True


def configure_logging(level: int, service_name: str) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.addFilter(_UvicornAccessFilter())
    handler.setFormatter(
        ecs_logging.StdlibFormatter(
            extra={"service": {"name": service_name}},
            exclude_fields=["log.original", "color_message"],
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [handler]
        uvicorn_logger.setLevel(level)
        uvicorn_logger.propagate = False
