import mysql.connector
from pydantic import (
    BaseModel,
    Field,
    model_serializer,
    ValidationError,
    field_validator,
)
from typing import Any


class Species(BaseModel):
    id: str = Field(alias="assembly.accession")
    common_name: str = Field(alias="species.common_name", default=None)
    scientific_name: str = Field(alias="species.scientific_name")
    assembly: str = Field(alias="assembly.default")
    assembly_accession: str = Field(alias="assembly.accession")
    unversioned_assembly_accession: str = Field(alias="assembly.accession")
    type_value: str = Field(alias="species.strain", default=None)
    parlance_name: str = Field(alias="species.parlance_name", default=None)
    type_type: str = Field(alias="strain.type", default=None)
    coding_genes: str = Field(alias="genebuild.coding_genes", default=None)
    n50: str = Field(alias="assembly.contig_n50", default=None)
    has_variation: bool = False
    has_regulation: bool = False
    annotation_method: str = Field(alias="genebuild.method", default=None)
    annotation_provider: str = Field(alias="annotation.provider_name", default=None)

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


mydb = mysql.connector.connect(
    host="mysql-ens-sta-6.ebi.ac.uk", port="4695", user="ensro"
)


mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES LIKE '%_core%_110_%'")

dbs = mycursor.fetchall()

species_data = []
for dbi in dbs:
    try:
        query = 'SELECT meta_key,meta_value FROM {db}.meta WHERE meta_key IN  ( "species.common_name", "species.scientific_name", "assembly.default", "assembly.accession", "genebuild.method","annotation.provider_name", "strain.type", "species.strain", "species.parlance_name", "assembly.contig_n50", "genebuild.coding_genes" );'.format(
            db=dbi[0]
        )
        mycursor.execute(query)
        myresult = {tv[0]: tv[1] for tv in mycursor.fetchall()}
        sd = Species(**myresult)
        species_data.append(sd)
    except Exception as ex:
        print(dbi[0], ex)
        pass
species_list = SpeciesList(
    species_list=species_data,
    name="ensemblNext",
    release="0.0.1",
    entry_count=len(species_data),
)
# ['Config', '__abstractmethods__', '__annotations__', '__class__', '__class_vars__', '__config__', '__custom_root_type__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__exclude_fields__', '__fields__', '__fields_set__', '__format__', '__ge__', '__get_validators__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__include_fields__', '__init__', '__init_subclass__', '__iter__', '__json_encoder__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__post_root_validators__', '__pre_root_validators__', '__pretty__', '__private_attributes__', '__reduce__', '__reduce_ex__', '__repr__', '__repr_args__', '__repr_name__', '__repr_str__', '__rich_repr__', '__schema_cache__', '__setattr__', '__setstate__', '__signature__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__try_update_forward_refs__', '__validators__', '_abc_impl', '_calculate_keys', '_copy_and_set_values', '_decompose_class', '_enforce_dict_if_root', '_get_value', '_init_private_attributes', '_iter', 'construct', 'copy', 'dict', 'from_orm', 'json', 'parse_file', 'parse_obj', 'parse_raw', 'schema', 'schema_json', 'species_list', 'update_forward_refs', 'validate']
print("Total : {}", len(species_data))

with open("ensemblnext_species_v3.json", "w") as sddf:
    sddf.write(species_list.model_dump_json())
