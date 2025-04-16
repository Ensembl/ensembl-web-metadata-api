import logging
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    validator,
    AliasChoices,
    AliasPath,
    field_serializer,
)

from core.logging import InterceptHandler
from core.config import ASSEMBLY_URLS

logging.getLogger().handlers = [InterceptHandler()]


class Type(BaseModel):
    kind: str
    value: str

    @field_serializer("value")
    def serialize_url(self, value: str):
        if value == "":
            return None
        return value


class Release(BaseModel):
    name: str = Field(alias="releaseLabel")
    type: str = Field(alias="releaseType")
    is_current: bool = Field(alias="isCurrent", default=False)


class AssemblyInGenome(BaseModel):
    accession_id: str = Field(alias="accession")
    name: str = Field(alias="name")
    url: str = Field(alias="accession", default=None)

    @validator("url", always=True)
    def generate_url(cls, value):
        if value.startswith("GCA"):
            return ASSEMBLY_URLS["GCA"] + value
        if value.startswith("GCF"):
            return ASSEMBLY_URLS["GCF"] + value
        return None


class AssemblyProvider(BaseModel):
    name: str
    url: str = Field(alias="url", default="")

    @field_serializer("url")
    def serialize_url(self, url: str):
        if url == "":
            return None
        return url


class AnnotationProvider(BaseModel):
    name: str
    url: str = Field(alias="url", default="")

    @field_serializer("url")
    def serialize_url(self, url: str):
        if url == "":
            return None
        return url


class BaseGenomeDetails(BaseModel):
    genome_id: str = Field(alias="genomeUuid")
    genome_tag: Optional[str] = Field(
        alias=AliasChoices(
            AliasPath("assembly", "urlName"), AliasPath("assembly", "tolId")
        ),
        default=None,
    )
    common_name: str = Field(alias=AliasPath("organism", "commonName"), default=None)
    scientific_name: str = Field(alias=AliasPath("organism", "scientificName"))
    type: Optional[Type] = None
    is_reference: bool = Field(
        alias=AliasPath("assembly", "isReference"), default=False
    )
    assembly: AssemblyInGenome = None
    release: Release = None


class BriefGenomeDetails(BaseGenomeDetails):
    """
    As mentioned in this PR: https://github.com/Ensembl/ensembl-web-metadata-api/pull/60
    We're planning to extend the BriefGenomeDetails class later
    """
    latest_genome: Optional[BaseGenomeDetails] = Field(alias="latestGenome", default=None)


class GenomeDetails(BaseGenomeDetails):
    taxonomy_id: str = Field(alias=AliasPath("organism", "taxonomyId"))
    species_taxonomy_id: str = Field(alias=AliasPath("organism", "speciesTaxonomyId"))
    assembly_provider: AssemblyProvider = None
    assembly_level: str = Field(alias=AliasPath("attributesInfo", "assemblyLevel"))
    assembly_date: str = Field(
        alias=AliasPath("attributesInfo", "assemblyDate"), default=None
    )
    annotation_provider: AnnotationProvider = None
    annotation_method: str = Field(
        alias=AliasPath("attributesInfo", "genebuildMethodDisplay"), default=None
    )
    annotation_version: str = Field(
        # TODO: remove genebuildVersion after the metadata DB is updated
        alias=AliasChoices(
            AliasPath("attributesInfo", "genebuildProviderVersion"),
            AliasPath("attributesInfo", "genebuildVersion")
        ),
        default=None
    )
    annotation_date: str = Field(alias="created", default=None)
    number_of_genomes_in_group: int = Field(alias="relatedAssembliesCount", default=1)

    @validator("taxonomy_id", "species_taxonomy_id", pre=True)
    def convert_int_to_str(cls, value):
        return str(value)

    @validator("annotation_date", pre=True)
    def parse_date(cls, value):
        year, month, _ = value.split("-")
        return year + "-" + month

    def __init__(self, **data):
        if data.get("organism", {}).get("strainType", None):
            data["type"] = {
                "kind": data.get("organism", {}).get("strainType", ""),
                "value": data.get("organism", {}).get("strain", ""),
            }
        if data.get("attributesInfo", {}).get("AssemblyProviderName", None):
            data["assembly_provider"] = {
                "name": data.get("attributesInfo", {}).get(
                    "assemblyProviderName", None
                ),
                "url": data.get("attributesInfo", {}).get("assemblyProviderUrl", ""),
            }
        if data.get("attributesInfo", {}).get("genebuildProviderName", None):
            data["annotation_provider"] = {
                "name": data.get("attributesInfo", {}).get(
                    "genebuildProviderName", None
                ),
                "url": data.get("attributesInfo", {}).get("genebuildProviderUrl", ""),
            }

        super().__init__(**data)


class DatasetAttribute(BaseModel):
    name: str = Field(alias="attributeName")
    value: str = Field(alias="attributeValue", default=None)
    version: str = Field(alias="datasetVersion")
    uuid: str = Field(alias="datasetUuid")
    type: str = Field(alias="datasetType")


class DatasetAttributes(BaseModel):
    attributes: list[DatasetAttribute]
    release_version: float = Field(alias="releaseVersion")

class GenomeByKeyword(BaseModel):
    genome_uuid: str = Field(alias="genomeUuid", default="")
    release_version: float = Field(alias=AliasPath("release", "releaseVersion"), default=0)
    genome_tag: str = Field(alias=AliasPath("assembly", "urlName"), default="")