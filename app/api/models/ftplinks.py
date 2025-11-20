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

from pydantic import BaseModel, Field, HttpUrl, field_serializer
from typing import Literal
from core.config import FTP_BASE_URL


class FTPLink(BaseModel):
    dataset: str = Field(..., validation_alias="datasetType")
    url: str = Field(..., validation_alias="path")

    @field_serializer("url")
    def url_serializer(self, path: str) -> HttpUrl:
        return f"{FTP_BASE_URL}{path}"


class FTPLinks(BaseModel):
    links: list[FTPLink] = Field(..., validation_alias="Links")
