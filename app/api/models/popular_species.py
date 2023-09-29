from pydantic import BaseModel, Field, AliasChoices, validator
from typing import List, Dict, Any, ClassVar


class PopularSpecies(BaseModel):
    _base_url: str = ClassVar[str]
    species_taxonomy_id: int = Field(alias="speciesTaxonomyId")
    name: str = Field(alias="commonName", validation_alias=AliasChoices('commonName', 'scientificName'))
    image: str = Field(alias="speciesTaxonomyId")
    genomes_count: int = Field(alias="count")

    @validator('image', pre=True)
    def generate_image_url(cls, v ) -> str:
        return '{}static/genome_images/{}.svg'.format(cls._base_url, v)

class PopularSpeciesGroup(BaseModel):
    _base_url: str
    popular_species: List[PopularSpecies]

    def __init__(self, **data):
        super().__init__(**data)
        PopularSpecies._base_url = data["_base_url"]
