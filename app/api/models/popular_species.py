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

from pydantic import BaseModel, Field, AliasChoices, validator
from typing import List, Dict, Any, ClassVar


class PopularSpecies(BaseModel):
    _base_url: str = ClassVar[str]
    species_taxonomy_id: str = Field(alias="speciesTaxonomyId")
    name: str = Field(alias="commonName", validation_alias=AliasChoices('commonName', 'scientificName'))
    image: str = Field(alias="speciesTaxonomyId")
    genomes_count: int = Field(alias="count")

    @validator('image', pre=True)
    def generate_image_url(cls, v ) -> str:
        return '{}static/genome_images/{}.svg'.format(cls._base_url, v)

    @validator("species_taxonomy_id", pre=True)
    def concert_int_to_str(cls, value):
        return str(value)

class PopularSpeciesGroup(BaseModel):
    _base_url: str
    popular_species: List[PopularSpecies]

    def __init__(self, **data):
        PopularSpecies._base_url = data["_base_url"]
        super().__init__(**data)
