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
    location_input: str
    genome_uuid: str = None
    name: str = Field(alias="name", default="")
    start: int = Field(alias="start", default=0)
    end: int = Field(alias="end", default=0)
    _region_code: str = None
    _is_valid: [bool, bool, bool] = [False, False, False]
    _region_name_em : str = None
    _start_em : str = None
    _end_em : str = None

    @root_validator(pre=True)
    def set_region_parameters(cls, values):
        parsed_region = cls.parse_location_input(values.get("location_input"))
        values["name"], values["start"], values["end"] = parsed_region
        return values

    def parse_location_input(rgn_input):
        rn, start, end = "", 0, 0
        logger.debug(rgn_input)
        try:
            rn_coords = rgn_input.split(":")
            if len(rn_coords) == 2:
                rn = rn_coords[0]
                start, end = rn_coords[1].split("-")
                start = start.replace(",","")
                end = end.replace(",","")
        except Exception as ex:
            logger.debug(ex)
        return (rn,start,end)


    def _validate_region_name(self):
        try:
            if self.name:
                genome_region = grpc_client.get_region(self.genome_uuid, self.name)
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
                    if genome_region.chromosomal:
                        self._region_code = "chromosome"
                    else:
                        self._region_code = "non-chormosome"
            else:
                self._is_valid[0] = False
                self._region_name_em = "Invalid region".format(self.location_input)
        except Exception as ex:
            logger.debug(ex)
            return False


    def validate_region(self):
        if self.genome_uuid:
                return True
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
        serialized_region["location"] = None


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
                serialized_region["location"] = "{}:{}-{}".format(self.name, self.start, self.end)
            else:
                serialized_region["location"] = None
        else:
            serialized_region["location"] = None
        return serialized_region
