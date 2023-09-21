from typing import List, Dict, Any
from json import JSONEncoder
import json
import sys
import configparser

import mysql.connector
from pydantic import BaseModel, Field, model_serializer, FieldValidationInfo, ValidationError, field_validator

class DefaultOnNoneModel(BaseModel):
    def __init__(self, **data):
        #Removes keys that have a value of None allowing the default to be selected
        data_without_none = {k:v for k,v in data.items() if (v is not None)}
        super().__init__(**data_without_none)

class Species(DefaultOnNoneModel):
    id: str = Field(alias="genome_uuid")
    common_name: str = Field(alias="common_name", default="")
    scientific_name: str = Field(alias="scientific_name", default="")
    assembly: str = Field(alias="assembly_default")
    assembly_accession: str = Field(alias="accession")
    unversioned_assembly_accession: str = Field(alias="accession")
    type_value: str = Field(alias="strain", default="")
    parlance_name: str = Field(alias="scientific_parlance_name", default="")
    type_type: str = Field(alias="strain_type", default="")
    coding_genes: str = Field(alias="coding_genes", default="0")
    n50: str = Field(alias="contig_n50", default="0")
    has_variation: bool = Field(default=False)
    has_regulation: bool = Field(default=False)
    annotation_method: str = Field(alias="genebuild_method", default="")
    annotation_provider: str = Field(alias="annotation_provider", default="")
    
    #New fields
    genome_uuid:str
    url_name: str = Field(default="")
    tol_id: str = Field(default="")
    is_reference:bool = Field(default=False) 
    species_taxonomy_id: int
    organism_id: int
    rank:int = Field(default="0")
    
    @model_serializer
    def serialise_species_model(self) -> Dict[str, Any]:
        species_json = [
            {"name": field_name, "value": field_value}
            for field_name, field_value in self
        ]

        return {"fields": species_json}

    @field_validator('unversioned_assembly_accession')
    @classmethod
    def make_unversioned_assembly_accession(cls, v: str) -> str:
        v = v.split('.')[0]
        return v

class SpeciesList(BaseModel):
    species_list: List[Species]
    name: str
    release: str
    # release_date: str
    entry_count: int

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        species_search_data = {}
        species_search_data["name"] = self.name
        species_search_data["release"] = self.release
        species_search_data["entry_count"] = self.entry_count
        species_search_data["entries"] = self.species_list
        return species_search_data


config = configparser.ConfigParser()
config.read('config.ini')

if "database" not in config.sections():
    print("Unable to find config.ini")
    sys.exit(-1)
    
db = config['database']

try:
    mydb = mysql.connector.connect(
        host=db.get('host',''),
        port=db.getint('port'),
        user=db.get('user',''),
        password=db.get('password',None),
        database=db.get('database','')
    )
except:
    print("Failed to connect to database")
    sys.exit(-1)

mycursor = mydb.cursor()

query = """
select distinct g.genome_uuid,
o.common_name,
o.scientific_name,
o.strain_type,
o.strain,
a.assembly_default,
a.accession,
a.url_name ,
a.tol_id,
a.is_reference,
a.name,
o.species_taxonomy_id,
o.scientific_parlance_name,
o.organism_id,
o.rank,
stats.contig_n50                                   as contig_n50,
stats.coding_genes                                 as coding_genes,
datasets.has_variation,
datasets.has_regulation,
ifnull(nullif(stats.provider_name, ''), 'Ensembl') as annotation_provider,
stats.genebuild_method                             as genebuild_method
from genome g
    join organism o using (organism_id)
    join assembly a using (assembly_id)
    left join organism_group_member ogm using (organism_id)
    left join organism_group og on (ogm.organism_group_id = og.organism_group_id and og.code = 'population')
    join (select g.genome_id,
                max(case when a.name = 'assembly.provider_name' then da.value else null end)   as provider_name,
                max(case when a.name = 'genebuild.method_display' then da.value else null end) as genebuild_method,
                max(case when a.name = 'genebuild.coding_genes' then da.value else null end)   as coding_genes,
                max(case when a.name = 'assembly.contig_n50' then da.value else null end)      as contig_n50#)
        from dataset_attribute da
                join attribute a on da.attribute_id = a.attribute_id
                join dataset d on da.dataset_id = d.dataset_id
                join genome_dataset gd on gd.dataset_id = d.dataset_id
                join genome g on g.genome_id = gd.genome_id
        where a.name in ('assembly.provider_name', 'genebuild.method_display', 'genebuild.coding_genes',
                        'assembly.contig_n50')
        group by g.genome_uuid) as stats on g.genome_id = stats.genome_id
    left join (select g.genome_id,
                    max(case when dt.name = 'regulation_build' then 1 else 0 end) as has_regulation,
                    max(case when dt.name = 'variation' then 1 else 0 end)       as has_variation
            from genome g
                        left join genome_dataset gd on gd.genome_id = g.genome_id
                        join dataset d on d.dataset_id = gd.dataset_id
                        join dataset_type dt on d.dataset_type_id = dt.dataset_type_id
            where dt.name in ('regulation_build', 'variation')) as datasets
            on datasets.genome_id = g.genome_id
order by a.assembly_default, o.rank, o.ensembl_name, a.assembly_id, g.genome_uuid;
"""

mycursor.execute(query)
columns = [desc[0] for desc in mycursor.description]
species_data = []

for row in mycursor.fetchall():
    dict_row = {columns[x]:row[x] for x in range(0,len(columns))}

    sd = Species(**dict_row)
    species_data.append(sd)

species_list = SpeciesList(
species_list=species_data,
name="ensemblNext",
release="0.0.2",
entry_count=len(species_data),
)

print(f"Total : {len(species_data)}")

with open("ensemblnext_species_v4.json", "w") as sddf:
    sddf.write(species_list.model_dump_json())
