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

from pydantic import BaseModel, validator, model_serializer, Field, root_validator
from typing import List, Dict, Any
from google.protobuf.json_format import MessageToDict
from loguru import logger
from core.config import GRPC_HOST, GRPC_PORT
from api.resources.grpc_client import GRPCClient

grpc_client = GRPCClient(GRPC_HOST, GRPC_PORT)


class RegionValidation(BaseModel):
    region_input: str
    genome_uuid: str = None
    name: str = Field(alias="name", default=None)
    start: int = Field(alias="start", default=0)
    end: int = Field(alias="end", default=0)
    _is_valid: [bool, bool, bool] = [False, False, False]
    _region_name_em : str = None
    _start_em : str = None
    _end_em : str = None

    @root_validator(pre=True)
    def set_region_parameters(cls, values):
        parsed_region = cls.parse_region_input(values.get("region_input"))
        values["name"], values["start"], values["end"] = parsed_region
        return values

    def parse_region_input(rgn_input):
        try:
            rn, coords = rgn_input.split(":")
            start, end = coords.split("-")
            logger.debug((rn,start,end))
            return (rn,start,end)
        except Exception as ex:
            logger.debug(ex)
        return (None, 0, 0)

    def _validate_region_name(self):
        try:
            if self.name:
                genome_region = grpc_client.get_region(self.genome_uuid, self.name)
                logger.debug(genome_region)
                if genome_region.ByteSize() == 0:
                    self._is_valid[0] = False
                    self._region_name_em = "Could not find region {} for {}".format(self.name, self.genome_uuid)
                else:
                    self._is_valid[0] = True
                    if self.start > 0 and self.start < genome_region.length :
                        self._is_valid[1] = True
                    else:
                        self._is_valid[1] = False
                        self._start_em = "start should be between 1 and {}".format(genome_region.length)
                    if self.end <= genome_region.length and self.end > self.start:
                        self._is_valid[2] = True
                    else:
                        self._is_valid[2] = False
                        self._end_em = "end should be between 1 and {} and end ({}) > start ({})".format(genome_region.length, self.end, self.start)
            else:
                self._is_valid[0] = False
                self._region_name_em = "Invalid region {}".format(self.name)
        except Exception as ex:
            logger.debug(ex)
            return False


    def validate_region(self):
        if self.genome_uuid:
            if self._validate_region_name():
                if self._validate_coordinates():
                    return True
                else:
                    return False
            else:
                return False
        return False

    def validate_region_name(self):
        try:
            genome_region = grpc_client.get_region(self.genome_uuid, self.name)
            return
        except Exception as ex:
            return False

    def validate_coords(self):
        pass

    @model_serializer
    def region_validation_serliaiser(self) -> Dict[str, Any]:
        default_response = {"error_code": None, "error_message": None}
        serialized_region = {}
        serialized_region["region"] = {"error_code": None, "error_message": None}
        serialized_region["start"] = {"error_code": None, "error_message": None}
        serialized_region["end"] = {"error_code": None, "error_message": None}
        serialized_region["region_id"] = None

        if self.genome_uuid:
            if self._is_valid[0] == True:
                serialized_region["region"]["region_name"] = self.name
                serialized_region["region"]["is_valid"] = True
            else:
                serialized_region["region"]["region_name"] = self.name
                serialized_region["region"]["is_valid"] = False
                serialized_region["region"]["error_message"] = self._region_name_em
            if self._is_valid[1]:
                serialized_region["start"]["value"] = self.start
                serialized_region["start"]["is_valid"] = True
            else:
                serialized_region["start"]["value"] = self.start
                serialized_region["start"]["is_valid"] = False
                serialized_region["start"]["error_message"] = self._start_em
            if self._is_valid[2]:
                serialized_region["end"]["value"] = self.end
                serialized_region["end"]["is_valid"] = True
            else:
                serialized_region["end"]["value"] = self.end
                serialized_region["end"]["is_valid"] = False
                serialized_region["end"]["error_message"] = self._end_em
            if all(self._is_valid):
                serialized_region["region_id"] = "{}:{}-{}".format(self.name, self.start, self.end)
            else:
                serialized_region["region_id"] = None
        else:
            serialized_region["region_id"] = None
        return serialized_region