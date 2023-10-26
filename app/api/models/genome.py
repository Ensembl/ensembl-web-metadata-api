import logging
from typing import Optional

from pydantic import BaseModel, Field, validator, AliasChoices, AliasPath

from core.logging import InterceptHandler
from core.config import ENA_ASSEMBLY_URL

logging.getLogger().handlers = [InterceptHandler()]


class Type(BaseModel):
    kind: str
    value: str


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
    name: str
    url: str


class AnnotationProvider(BaseModel):
    name: str
    url: str


class GenomeDetails(BaseModel):
    genome_id: str = Field(alias='genomeUuid')
    genome_tag: Optional[str] = Field(
        alias=AliasChoices(AliasPath('assembly', 'urlName'), AliasPath('assembly', 'tolId')), default=None)
    taxonomy_id: str = Field(alias=AliasPath('organism', 'taxonomyId'))
    species_taxonomy_id: str = Field(alias=AliasPath('organism', 'speciesTaxonomyId'))
    common_name: str  = Field(alias=AliasPath('organism', 'commonName'), default=None)
    scientific_name: str = Field(alias=AliasPath('organism', 'scientificName'))
    type: Optional[Type] = None
    is_reference: bool = Field(alias=AliasPath('assembly', 'isReference'),default=False)
    assembly: AssemblyInGenome = None
    assembly_provider: AssemblyProvider = None
    assembly_level: str = Field(alias=AliasPath('attributesInfo', 'assemblyLevel'))
    assembly_date: str = Field(alias=AliasPath('attributesInfo', 'assemblyDate'))
    annotation_provider: AnnotationProvider = None
    annotation_method: str = Field(alias='genebuildMethod', default=None)  # REMOVE DEFAULT
    annotation_version: str = Field(alias='genebuildVersion', default=None)
    annotation_date: str = Field(alias='created')
    number_of_genomes_in_group: int = Field(alias='relatedAssembliesCount', default=1)

    @validator("taxonomy_id", "species_taxonomy_id", pre=True)
    def concert_int_to_str(cls, value):
        return str(value)

    @validator("annotation_date", pre=True)
    def parse_date(cls, value):
        year, month, _ = value.split("-")
        return year + '-' + month

    def __init__(self, **data):
        if data.get("organism", {}).get('strainType', None):
            data["type"] = {
                "kind": data.get("organism", {}).get("strainType", None),
                "value": data.get("organism", {}).get("strain", None),
            }
        if data.get("attributesInfo", {}).get('AssemblyProviderName', None):  # TODO: Update attributesInfo
            data["assembly_provider"] = {
                "name": data.get("attributesInfo", {}).get("AssemblyProviderName", None),
                "url": data.get("attributesInfo", {}).get("AssemblyProviderUrl", None),
            }
        if data.get("attributesInfo", {}).get('annotationProviderName', None):
            data["annotation_provider"] = {
                "name": data.get("attributesInfo", {}).get("annotationProviderName", None),
                "url": data.get("attributesInfo", {}).get("annotationProviderUrl", None),
            }

        super().__init__(**data)
