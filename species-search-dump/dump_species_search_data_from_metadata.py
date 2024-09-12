from typing import Any
import sys
import configparser

import mysql.connector
from pydantic import (
    BaseModel,
    Field,
    model_serializer,
    ValidationError,
    field_validator,
    model_validator,
)


class DefaultOnNoneModel(BaseModel):
    def __init__(self, **data):
        # Removes keys that have a value of None allowing the default to be selected
        data_without_none = {k: v for k, v in data.items() if (v is not None)}
        super().__init__(**data_without_none)


class Species(DefaultOnNoneModel):
    id: str = Field(alias="genome_uuid")
    common_name: str = Field(alias="common_name", default="")
    scientific_name: str = Field(alias="scientific_name")
    assembly: str = Field(alias="assembly_name")
    assembly_accession: str = Field(alias="accession")
    unversioned_assembly_accession: str = Field(alias="accession")
    type_value: str = Field(alias="strain", default="")
    parlance_name: str = Field(alias="scientific_parlance_name", default="")
    type_type: str = Field(alias="strain_type", default="")
    coding_genes: str = Field(alias="coding_genes", default="0")
    n50: str = Field(alias="contig_n50", default="0")
    has_variation: bool = Field(default=False)
    has_regulation: bool = Field(default=False)
    annotation_method: str = Field(alias="genebuild_method")
    annotation_provider: str = Field(alias="genebuild_provider")

    # New fields
    genome_uuid: str
    url_name: str = Field(default="")
    tol_id: str = Field(default="")
    is_reference: bool = Field(default=False)
    species_taxonomy_id: int
    organism_id: int
    rank: int = Field(default="0")

    @model_serializer
    def serialise_species_model(self) -> dict[str, Any]:
        species_json = [
            {"name": field_name, "value": field_value}
            for field_name, field_value in self
        ]
        return {"fields": species_json}

    @field_validator("unversioned_assembly_accession")
    @classmethod
    def make_unversioned_assembly_accession(cls, v: str) -> str:
        v = v.split(".")[0]
        return v

    @model_validator(mode="after")
    def clean_up_type(self) -> "Species":
        if len(self.type_type) == 0:
            self.type_value = ""
            print(
                f"Cleared type for {self.scientific_name} - {self.id} due to type_type"
            )
        elif len(self.type_value) == 0:
            self.type_type = ""
            print(
                f"Cleared type for {self.scientific_name} - {self.id} due to type_value"
            )
        return self


class SpeciesList(BaseModel):
    species_list: list[Species]
    name: str
    release: str
    # release_date: str
    entry_count: int

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        species_search_data = {}
        species_search_data["name"] = self.name
        species_search_data["release"] = self.release
        species_search_data["entry_count"] = self.entry_count
        species_search_data["entries"] = self.species_list
        return species_search_data


def clean_value(val):
    """Used to set known representations of null in the data coming from metadata to None"""
    known_data_errors = ["NULL", '"NA"']
    if val in known_data_errors:
        return None
    return val


def dump_species():
    config = configparser.ConfigParser()
    config.read("config.ini")

    if "database" not in config.sections():
        print("Unable to find config.ini")
        sys.exit(-1)

    db = config["database"]

    try:
        mydb = mysql.connector.connect(
            host=db.get("host", ""),
            port=db.getint("port"),
            user=db.get("user", ""),
            password=db.get("password", None),
            database=db.get("database", ""),
        )
    except:
        print("Failed to connect to database")
        sys.exit(-1)

    mycursor = mydb.cursor()

    query = """SELECT 
    genome_uuid,
    common_name,
    scientific_name,
    strain_type,
    strain,
    assembly_name,
    accession,
    url_name,
    tol_id,
    is_reference,
    name,
    species_taxonomy_id,
    scientific_parlance_name,
    organism_id,
    rank,
    contig_n50,
    coding_genes,
    has_variation,
    has_regulation,
    genebuild_provider,
    genebuild_method
    from genome_search"""

    mycursor.execute(query)
    columns = [desc[0] for desc in mycursor.description]
    species_data = []

    for row in mycursor.fetchall():
        dict_row = {columns[x]: clean_value(row[x]) for x in range(0, len(columns))}

        try:
            sd = Species(**dict_row)
            species_data.append(sd)

        except ValidationError as err:
            print(f"Unable to validate {dict_row['scientific_name']}")
            print(f"Errors found {err.error_count()}")
            for e in err.errors():
                print(f"{e['type']}: {e['loc']}")

    species_list = SpeciesList(
        species_list=species_data,
        name="ensemblNext",
        release="0.0.3",
        entry_count=len(species_data),
    )

    print(f"Total : {len(species_data)}")

    with open("ensemblnext_species.json", "w") as sddf:
        sddf.write(species_list.model_dump_json())


if __name__ == "__main__":
    dump_species()
