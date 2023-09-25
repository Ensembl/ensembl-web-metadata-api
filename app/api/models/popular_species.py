from pydantic import BaseModel, Field, field_serializer, model_serializer, field_validator,  AliasChoices
from typing import List, Dict, Any


class PopularSpecies(BaseModel):
    species_taxonomy_id: int = Field(alias="speciesTaxonomyId", default=None)
    name: str = Field(alias="commonName", validation_alias=AliasChoices('commonName', 'scientificName'))
    image: str = Field(alias="image")
    genomes_count: int = Field(alias="count", default=None)

class PopularSpeciesGroup(BaseModel):
    popular_species: List[PopularSpecies]