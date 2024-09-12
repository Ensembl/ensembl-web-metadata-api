"""
.. See the NOTICE file distributed with this work for additional information
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
from pydantic import BaseModel, model_serializer, Field, root_validator
from typing import Any, Optional

from core.config import GRPC_HOST, GRPC_PORT
from api.resources.grpc_client import GRPCClient
from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]

grpc_client = GRPCClient(GRPC_HOST, GRPC_PORT)


class RegionValidation(BaseModel):
    location_input: str
    genome_uuid: str = None
    name: str = Field(alias="name", default="")
    start: str = Field(alias="start", default="1")
    end: Optional[str] = Field(alias="end", default=None)
    _region_code: str = None
    _is_valid: list[bool] = [False, False, False]
    _region_name_error: str = None
    _start_error: str = None
    _end_error: str = None

    @root_validator(pre=True)
    def set_region_parameters(cls, values):
        parsed_region = cls.parse_location_input(values.get("location_input"))
        values["name"], values["start"], values["end"] = parsed_region
        return values

    @staticmethod
    def parse_location_input(region_input):
        region, start, end = "", "1", None
        try:
            region_coordinates = region_input.split(":")
            region = region_coordinates[0]
            start, end = region_coordinates[1].split("-")
            start = start.replace(",", "")
            end = end.replace(",", "")
        except IndexError:
            pass
        except Exception as ex:
            logging.error(ex)
        return region, start, end

    def _validate_region_name(self):
        if self.name:
            try:
                genome_region = grpc_client.get_region(self.genome_uuid, self.name)
                if self.end is None:
                    self.end = genome_region.length
                if genome_region.ByteSize() == 0:
                    self._is_valid[0] = False
                    self._region_name_error = "Could not find region {} for {}".format(
                        self.name, self.genome_uuid
                    )
                    return False
                else:
                    self._is_valid[0] = True
                    if genome_region.chromosomal:
                        self._region_code = "chromosome"
                    else:
                        self._region_code = "non-chormosome"
            except Exception as ex:
                logging.error(ex)
                return False

            try:
                start_value = int(self.start)
                if (start_value > 0) and (start_value < genome_region.length):
                    self._is_valid[1] = True
                else:
                    self._is_valid[1] = False
                    self._start_error = "start should be between 1 and {}".format(
                        genome_region.length
                    )
            except ValueError as ve:
                self._is_valid[1] = False
                self._start_error = "start {} is invalid".format(self.start)

            try:
                end_value = int(self.end)
                if self._is_valid[1]:
                    if (end_value <= genome_region.length) and (end_value > start_value):
                        self._is_valid[2] = True
                    else:
                        self._is_valid[2] = False
                        self._end_error = "end should be between 1 and {} and end ({}) > start ({})".format(
                            genome_region.length, self.end, self.start
                        )
            except ValueError as ve:
                self._is_valid[2] = False
                self._end_error = "end {} is invalid".format(self.end)
        else:
            self._is_valid[0] = False
            self._region_name_error = "Invalid region".format(self.location_input)

        return all(self._is_valid)

    def validate_region(self):
        if self.genome_uuid:
            if self._validate_region_name():
                return True
            else:
                return False
        return False

    @model_serializer
    def region_validation_serliaiser(self) -> dict[str, Any]:
        serialized_region = {
            "region": {"error_code": None, "error_message": None},
            "start": {"error_code": None, "error_message": None},
            "end": {"error_code": None, "error_message": None},
            "location": None,
        }

        if self.genome_uuid:
            if self._is_valid[0]:
                serialized_region["region"]["region_name"] = self.name
                serialized_region["region"]["is_valid"] = True
            else:
                serialized_region["region"]["region_name"] = self.name
                serialized_region["region"]["is_valid"] = False
                serialized_region["region"]["error_message"] = self._region_name_error
            if self._is_valid[1]:
                serialized_region["start"]["value"] = int(self.start)
                serialized_region["start"]["is_valid"] = True
            else:
                serialized_region["start"]["value"] = self.start
                serialized_region["start"]["is_valid"] = False
                serialized_region["start"]["error_message"] = self._start_error
            if self._is_valid[2]:
                serialized_region["end"]["value"] = int(self.end)
                serialized_region["end"]["is_valid"] = True
            else:
                serialized_region["end"]["value"] = self.end
                serialized_region["end"]["is_valid"] = False
                serialized_region["end"]["error_message"] = self._end_error
            if all(self._is_valid):
                serialized_region["location"] = "{}:{}-{}".format(
                    self.name, self.start, self.end
                )
            else:
                serialized_region["location"] = None
        else:
            serialized_region["location"] = None
        return serialized_region
