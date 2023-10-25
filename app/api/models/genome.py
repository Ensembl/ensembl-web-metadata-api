import logging
from typing import Optional

from pydantic import BaseModel, Field, validator

from core.logging import InterceptHandler
from core.config import ENA_ASSEMBLY_URL

logging.getLogger().handlers = [InterceptHandler()]


class Type(BaseModel):
    kind: str = Field(alias='kind')
    value: str = Field(alias='value')


class AssemblyInGenome(BaseModel):
    accession_id: str = Field(alias='accession')
    name: str = Field(alias='name')
    url: str = Field(alias='accession', default=None)

    @validator("url", always=True)
    def generate_url(cls, value):
        if value and "GCA" in value:
            return ENA_ASSEMBLY_URL + value
        return None


class AssemblyProvider(BaseModel):
    name: str = Field(alias='', default=None)  # REMOVE DEFAULT
    url: str = Field(alias='', default=None)


class AnnotationProvider(BaseModel):
    name: str = Field(alias='annotationProviderName', default=None)  # REMOVE DEFAULT
    url: str = Field(alias='annotationProviderUrl', default=None)


class GenomeDetails(BaseModel):
    genome_id: str = Field(alias='genomeUuid')
    genome_tag: Optional[str] = Field(alias='assembly', default=None)
    taxonomy_id: str
    species_taxonomy_id: str
    common_name: str = None
    scientific_name: str
    type: Optional[Type] = Field(alias='type', default=None)
    is_reference: bool = Field(alias='isReference', default=False)
    assembly: AssemblyInGenome = None
    assembly_provider: AssemblyProvider = None
    assembly_level: str
    assembly_date: str
    annotation_provider: AnnotationProvider = Field(alias='attributesInfo', default=None)
    annotation_method: str = Field(alias='genebuildMethod', default=None)  # REMOVE DEFAULT
    annotation_version: str = Field(alias='genebuildVersion', default=None)
    annotation_date: str = Field(alias='created')
    number_of_genomes_in_group: int = Field(alias='relatedAssembliesCount', default=1)

    @validator("annotation_date", pre=True)
    def parse_birthdate(cls, value):
        year, month, _ = value.split("-")
        return year + '-' + month

    @validator("genome_tag", pre=True)
    def fetch_genome_tag_value(cls, value):
        if value and type(value) is dict:
            if value.get("urlName", None):
                return value.get("urlName", None)
            return value.get("tolId", None)
        return value

    def __init__(self, **data):

        if data.get("organism", {}).get('strainType', None):
            data["type"] = {
                "kind": data.get("strainType", None),
                "value": data.get("strain", None),
            }
        data["taxonomy_id"] = str(data.get("organism", {}).get("taxonomyId"))
        data["species_taxonomy_id"] = str(data.get("organism", {}).get("speciesTaxonomyId", None))
        data["common_name"] = data.get("organism", {}).get("commonName", None)
        data["scientific_name"] = data.get("organism", {}).get("scientificName", None)
        data["isReference"] = data.get("assembly", {}).get('isReference', False)
        data["assembly_level"] = data.get("attributesInfo", {}).get('assemblyLevel')
        data["assembly_date"] = data.get("attributesInfo", {}).get('assemblyDate', None)

        super().__init__(**data)
