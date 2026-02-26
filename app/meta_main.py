"""
See the NOTICE file distributed with this work for additional information
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

import enum
import itertools
import logging
from core.logging import InterceptHandler
import os
import pprint
import pytest
import sqlalchemy
import time
import timeit
import uuid
from datetime import datetime

from typing import Annotated, Type, Any

from fastapi import APIRouter, Request, responses, Query, Path, FastAPI, Depends
from fastapi.testclient import TestClient

from pydantic import ValidationError

from sqlalchemy import Column, Integer, create_engine, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm.session import Session

from api.error_response import response_error_handler
from api.models.checksums import Checksum
from api.models.ftplinks import FTPLinks
from api.models.genome import BriefGenomeDetails, GenomeDetails, DatasetAttributes, GenomeByKeyword, Release, GenomeGroupsResponse, GenomesInGroupResponse, GenomeCountsResponse
from api.models.karyotype import Karyotype
from api.models.popular_species import PopularSpeciesGroup
from api.models.region_validation import RegionValidation
from api.models.statistics import GenomeStatistics, ExampleObjectList
from api.models.vep import VepFilePaths

from ensembl.production.metadata.api.adaptors import GenomeAdaptor, ReleaseAdaptor
from ensembl.production.metadata.api.adaptors.vep import VepAdaptor
from ensembl.production.metadata.api.models import Genome
from ensembl.production.metadata.grpc.config import MetadataConfig

from ensembl.utils.database import DBConnection

#from api.resources.redis import redis_cache


TEST_DB_URL = "duckdb:///./duck_meta.db"
meta_conn = DBConnection(TEST_DB_URL)
genome_adaptor = GenomeAdaptor(meta_conn)
vep_adaptor = VepAdaptor(meta_conn)
release_adaptor = ReleaseAdaptor(meta_conn)

def get_genome_adaptor():
	yield genome_adaptor

def get_vep_adaptor():
	yield vep_adaptor

def get_release_adaptor():
	yield release_adaptor

GenomeAdaptorDep = Annotated[GenomeAdaptor, Depends(get_genome_adaptor)]
VepAdaptorDep = Annotated[VepAdaptor, Depends(get_vep_adaptor)]
ReleaseAdaptorDep = Annotated[ReleaseAdaptor, Depends(get_release_adaptor)]

logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()

logging.info("Starting up")

# TODO
logger = logging


# OK
def get_species_information(db_conn, genome_uuid):
    if not genome_uuid:
        logger.warning("Missing or Empty Genome UUID field.")
        return None
    species_results = db_conn.fetch_genomes(genome_uuid=genome_uuid)
    # TODO Patchy updates to fetch only the first one from results in case the genome is in multiple
    #  release == strongly based on assertion that results are ordered by EnsemblRelease.version.desc()
    if len(species_results) == 0:
        logger.error(f"Species not found for genome {genome_uuid}")
        return None
    else:
        if len(species_results) > 1:
            logger.warning(f"Multiple results returned for {genome_uuid}.")
        tax_id = species_results[0].Organism.taxonomy_id
        taxo_results = db_conn.fetch_taxonomy_names(tax_id)
        response_data = (species_results[0], taxo_results[tax_id])
        return response_data


# OK
def is_valid_uuid(value):
    try:
        # Attempt to create a UUID object from the input
        uuid_obj = uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


# OK
def get_alternative_names(db_conn, taxon_id):
    """ Get alternative names for a given taxon ID """
    taxon_ifo = db_conn.fetch_taxonomy_names(taxon_id)
    alternative_names = taxon_ifo[taxon_id].get('synonym')
    genbank_common_name = taxon_ifo[taxon_id].get('genbank_common_name')

    if genbank_common_name is not None:
        alternative_names.append(genbank_common_name)

    # remove duplicates
    unique_alternative_names = list(set(alternative_names))
    # sort before returning (otherwise the test breaks)
    sorted_unique_alternative_names = sorted(unique_alternative_names)
    return sorted_unique_alternative_names




# TODO
def get_genome_groups_by_reference(
    db_conn: Any,
    group_type: str,
    release_label: str | None = None,
):
    if not group_type or group_type != 'structural_variant': # accepting only structural_variant for now
        logger.warning("Missing or Wrong Group type field.")
        return msg_factory.create_genome_groups_by_reference()

    # The logic calling the ORM and fetching data from the DB
    # will go here, we are returning dummy data for now
    # /!\ Remember to handle the release label

    try:
        # The logic calling the ORM and fetching data from the DB
        # will go here. For now, we return dummy data.
        dummy_data = [
            {
                "group_id": "grch38-group",
                "group_type": group_type,
                "group_name": "",
                "reference_genome": {
                    "genome_uuid": "a7335667-93e7-11ec-a39d-005056b38ce3",
                    "assembly": {
                        "accession": "GCA_000001405.29",
                        "name": "GRCh38.p14",
                        "ucsc_name": "hg38",
                        "level": "chromosome",
                        "ensembl_name": "GRCh38.p14",
                        "assembly_uuid": "fd7fea38-981a-4d73-a879-6f9daef86f08",
                        "is_reference": True,
                        "url_name": "grch38",
                        "tol_id": "",
                    },
                    "taxon": {
                        "taxonomy_id": 9606,
                        "scientific_name": "Homo sapiens",
                        "strain": "",
                        "alternative_names": [],
                    },
                    "created": "2023-09-22 15:04:45",
                    "organism": {
                        "common_name": "Human",
                        "strain": "",
                        "scientific_name": "Homo sapiens",
                        "ensembl_name": "SAMN12121739",
                        "scientific_parlance_name": "Human",
                        "organism_uuid": "1d336185-affe-4a91-85bb-04ebd73cbb56",
                        "strain_type": "",
                        "taxonomy_id": 9606,
                        "species_taxonomy_id": 9606,
                    },
                    "release": {
                        "release_version": 1,
                        "release_date": "2025-02-27",
                        "release_label": "2025-02",
                        "release_type": "integrated",
                        "is_current": True,
                        "site_name": "Ensembl",
                        "site_label": "MVP ENsembl",
                        "site_uri": "https://beta.ensembl.org",
                    },
                },
            },
            {
                "group_id": "t2t-group",
                "group_type": group_type,
                "group_name": "",
                "reference_genome": {
                    "genome_uuid": "4c07817b-c7c5-463f-8624-982286bc4355",
                    "assembly": {
                        "accession": "GCA_009914755.4",
                        "name": "T2T-CHM13v2.0",
                        "ucsc_name": "",
                        "level": "primary_assembly",
                        "ensembl_name": "T2T-CHM13v2.0",
                        "assembly_uuid": "fc20ebd6-f756-45da-b941-b3b17e11515f",
                        "is_reference": False,
                        "url_name": "t2t-chm13",
                        "tol_id": "",
                    },
                    "taxon": {
                        "taxonomy_id": 9606,
                        "scientific_name": "Homo sapiens",
                        "strain": "",
                        "alternative_names": [],
                    },
                    "created": "2023-09-22 15:06:39",
                    "organism": {
                        "common_name": "Human",
                        "strain": "",
                        "scientific_name": "Homo sapiens",
                        "ensembl_name": "SAMN03255769",
                        "scientific_parlance_name": "Human",
                        "organism_uuid": "9df68864-e9fe-4c02-ab8c-8190baad16c6",
                        "strain_type": "",
                        "taxonomy_id": 9606,
                        "species_taxonomy_id": 9606,
                    },
                    "release": {
                        "release_version": 1,
                        "release_date": "2025-02-27",
                        "release_label": "2025-02",
                        "release_type": "integrated",
                        "is_current": True,
                        "site_name": "Ensembl",
                        "site_label": "MVP ENsembl",
                        "site_uri": "https://beta.ensembl.org",
                    },
                },
            },
        ]

        # Very simple use of release_label even in dummy mode
        # TODO: move this filtering into the ORM query once the real implementation is added.
        if release_label:
            dummy_data = [
                g
                for g in dummy_data
                if g["reference_genome"]["release"]["release_label"] == release_label
            ]

        return msg_factory.create_genome_groups_by_reference(dummy_data)

    except Exception:
        # Dummy error handling until the real ORM logic is in place
        logger.exception(
            "Unexpected error while fetching genome groups "
            "(group_type=%r, release_label=%r)",
            group_type,
            release_label,
        )
        # Return an empty message to avoid propagating the error to callers.
        return msg_factory.create_genome_groups_by_reference([])


# TODO
def get_genomes_in_group(
    db_conn: Any,
    group_id: str,
    release_label: str | None,
):
    if not group_id:
        logger.warning("Missing or Empty Group type field.")
        return msg_factory.create_genomes_in_group()

    try:
        # The logic calling the ORM and fetching data from the DB using group_id
        # will go here. We return dummy data for now.
        # /!\ Remember to handle the release label in the real query.

        # TODO: remove this once we have the real data from the DB.
        dummy_data = [
            {
                "genome_uuid": "a7335667-93e7-11ec-a39d-005056b38ce3",
                "assembly": {
                    "accession": "GCA_000001405.29",
                    "name": "GRCh38.p14",
                    "ucsc_name": "hg38",
                    "level": "chromosome",
                    "ensembl_name": "GRCh38.p14",
                    "assembly_uuid": "fd7fea38-981a-4d73-a879-6f9daef86f08",
                    "is_reference": True,
                    "url_name": "grch38",
                    "tol_id": "",
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "",
                    "alternative_names": [],
                },
                "created": "2023-09-22 15:04:45",
                "organism": {
                    "common_name": "Human",
                    "strain": "",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN12121739",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "1d336185-affe-4a91-85bb-04ebd73cbb56",
                    "strain_type": "",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606,
                },
                "release": {
                    "release_version": 1,
                    "release_date": "2025-02-27",
                    "release_label": "2025-02",
                    "release_type": "integrated",
                    "is_current": True,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org",
                },
            },
            {
                "genome_uuid": "4c07817b-c7c5-463f-8624-982286bc4355",
                "assembly": {
                    "accession": "GCA_009914755.4",
                    "name": "T2T-CHM13v2.0",
                    "ucsc_name": "",
                    "level": "primary_assembly",
                    "ensembl_name": "T2T-CHM13v2.0",
                    "assembly_uuid": "fc20ebd6-f756-45da-b941-b3b17e11515f",
                    "is_reference": False,
                    "url_name": "t2t-chm13",
                    "tol_id": "",
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "",
                    "alternative_names": [],
                },
                "created": "2023-09-22 15:06:39",
                "organism": {
                    "common_name": "Human",
                    "strain": "",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN03255769",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "9df68864-e9fe-4c02-ab8c-8190baad16c6",
                    "strain_type": "",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606,
                },
                "release": {
                    "release_version": 1,
                    "release_date": "2025-02-27",
                    "release_label": "2025-02",
                    "release_type": "integrated",
                    "is_current": True,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org",
                },
            },
            {
                "genome_uuid": "9d3b2ead-a987-4f08-8d18-10a1eb1e0fb0",
                "assembly": {
                    "accession": "GCA_018503275.2",
                    "name": "NA19240_mat_hprc_f2",
                    "ucsc_name": "",
                    "level": "primary_assembly",
                    "ensembl_name": "",
                    "assembly_uuid": "561a1451-cfe4-451d-ad8f-00310645e1fd",
                    "is_reference": False,
                    "url_name": "",
                    "tol_id": ""
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "Yoruban in Nigeria",
                    "alternative_names": []
                },
                "created": "2025-09-23 19:07:22",
                "organism": {
                    "common_name": "Human",
                    "strain": "Yoruban in Nigeria",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN03838746",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "14a967b2-6d62-49f8-b0b7-c3836a87cffa",
                    "strain_type": "population",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606
                },
                "release": {
                    "release_version": 114.9,
                    "release_date": "2025-10-21",
                    "release_label": "2025-10-21",
                    "release_type": "partial",
                    "is_current": False,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org"
                }
            },
            {
                "genome_uuid": "27be510b-c431-434c-a6f5-158d8c138507",
                "assembly": {
                    "accession": "GCA_018506975.2",
                    "name": "HG00733_mat_hprc_f2",
                    "ucsc_name": "",
                    "level": "primary_assembly",
                    "ensembl_name": "",
                    "assembly_uuid": "0fb76cdf-6c6b-4c20-beef-7f7d4151651b",
                    "is_reference": False,
                    "url_name": "",
                    "tol_id": ""
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "Puerto Rican in Puerto Rico",
                    "alternative_names": []
                },
                "created": "2025-09-23 22:58:45",
                "organism": {
                    "common_name": "Human",
                    "strain": "Puerto Rican in Puerto Rico",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN00006581",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "07314e4e-9ac5-4ed7-b2ae-b8e257e1e6d7",
                    "strain_type": "population",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606
                },
                "release": {
                    "release_version": 114.9,
                    "release_date": "2025-10-21",
                    "release_label": "2025-10-21",
                    "release_type": "partial",
                    "is_current": False,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org"
                }
            },
            {
                "genome_uuid": "7e09bad9-aa22-46e4-ab8f-1b2a64202967",
                "assembly": {
                    "accession": "GCA_042077495.1",
                    "name": "NA19036_hap1_hprc_f2",
                    "ucsc_name": "",
                    "level": "primary_assembly",
                    "ensembl_name": "",
                    "assembly_uuid": "11ed863b-5b0a-45e6-b3e6-f0788be79706",
                    "is_reference": False,
                    "url_name": "",
                    "tol_id": ""
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "",
                    "alternative_names": []
                },
                "created": "2025-03-14 00:00:45",
                "organism": {
                    "common_name": "Human",
                    "strain": "",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN41021642",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "eec7d10e-3ef4-4f14-8d2e-3233978dd0ce",
                    "strain_type": "",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606
                },
                "release": {
                    "release_version": 114.1,
                    "release_date": "2025-05-28",
                    "release_label": "2025-05-28",
                    "release_type": "partial",
                    "is_current": False,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org"
                }
            },
            {
                "genome_uuid": "30094672-c48c-425a-84e0-4049073a68d3",
                "assembly": {
                    "accession": "GCA_018469665.2",
                    "name": "HG01123_mat_hprc_f2",
                    "ucsc_name": "",
                    "level": "primary_assembly",
                    "ensembl_name": "",
                    "assembly_uuid": "6ab0e3a4-4e11-443d-a18a-81ff1e68d42d",
                    "is_reference": False,
                    "url_name": "",
                    "tol_id": ""
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "Colombian in Medellin",
                    "alternative_names": []
                },
                "created": "2025-09-24 11:47:25",
                "organism": {
                    "common_name": "Human",
                    "strain": "Colombian in Medellin",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN17861232",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "c9bd9d75-c746-4515-ad37-40d054eeaa91",
                    "strain_type": "population",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606
                },
                "release": {
                    "release_version": 114.9,
                    "release_date": "2025-10-21",
                    "release_label": "2025-10-21",
                    "release_type": "partial",
                    "is_current": False,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org"
                }
            },
            {
                "genome_uuid": "82b440be-8f7d-47fe-a363-a40cea709ea2",
                "assembly": {
                    "accession": "GCA_018472595.2",
                    "name": "HG00438_pat_hprc_f2",
                    "ucsc_name": "",
                    "level": "primary_assembly",
                    "ensembl_name": "",
                    "assembly_uuid": "179f190d-17f9-4692-9353-374976c62e20",
                    "is_reference": False,
                    "url_name": "",
                    "tol_id": ""
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "Han Chinese South",
                    "alternative_names": []
                },
                "created": "2025-09-25 09:01:42",
                "organism": {
                    "common_name": "Human",
                    "strain": "Han Chinese South",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN17861652",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "b6f5e927-22f1-4e12-8bc5-77880de41211",
                    "strain_type": "population",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606
                },
                "release": {
                    "release_version": 114.9,
                    "release_date": "2025-10-21",
                    "release_label": "2025-10-21",
                    "release_type": "partial",
                    "is_current": False,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org"
                }
            },
            {
                "genome_uuid": "ddfadcb5-3b4a-48ca-9dcd-e75884445bd1",
                "assembly": {
                    "accession": "GCA_018472695.2",
                    "name": "HG01928_mat_hprc_f2",
                    "ucsc_name": "",
                    "level": "primary_assembly",
                    "ensembl_name": "",
                    "assembly_uuid": "c4b526fd-4919-459f-b25e-9f1f658e0c53",
                    "is_reference": False,
                    "url_name": "",
                    "tol_id": ""
                },
                "taxon": {
                    "taxonomy_id": 9606,
                    "scientific_name": "Homo sapiens",
                    "strain": "Peruvian in Lima",
                    "alternative_names": []
                },
                "created": "2025-09-26 17:12:04",
                "organism": {
                    "common_name": "Human",
                    "strain": "Peruvian in Lima",
                    "scientific_name": "Homo sapiens",
                    "ensembl_name": "SAMN17861660",
                    "scientific_parlance_name": "Human",
                    "organism_uuid": "c0ce970e-a1ab-492e-8838-684854ed22fb",
                    "strain_type": "population",
                    "taxonomy_id": 9606,
                    "species_taxonomy_id": 9606
                },
                "release": {
                    "release_version": 114.9,
                    "release_date": "2025-10-21",
                    "release_label": "2025-10-21",
                    "release_type": "partial",
                    "is_current": False,
                    "site_name": "Ensembl",
                    "site_label": "MVP ENsembl",
                    "site_uri": "https://beta.ensembl.org"
                }
            }
        ]

        # Use release_label even in dummy mode: filter to matching releases.
        if release_label:
            dummy_data = [
                g
                for g in dummy_data
                if "release" in g
                   and g["release"].get("release_label") == release_label
            ]

        return msg_factory.create_genomes_in_group(dummy_data)

    except Exception:
        # Dummy error handling until ORM logic is implemented.
        logger.exception(
            "Unexpected error while fetching genomes in group "
            "(group_id=%r, release_label=%r)",
            group_id,
            release_label,
        )
        return msg_factory.create_genomes_in_group([])


# END TODO


def create_genome(data=None, attributes=None, count=0, alternative_names=[], datasets=[]):
    if data is None:
            return None

    assembly = create_assembly(data)
    taxon = create_taxon(data, alternative_names)
    organism = create_organism(data)
    attributes_info = create_attributes_info(attributes)
    release = create_release(data)

    available_datasets = list({ds_type.dataset.dataset_type.name for ds_type in datasets})

    genome = {
        'genome_uuid':data.Genome.genome_uuid,
        'created':str(data.Genome.created),
        'assembly':assembly,
        'taxon':taxon,
        'organism':organism,
        'attributes_info':attributes_info,
        'release':release,
        'related_assemblies_count':count,
        'available_datasets':available_datasets
    }
    return genome


def create_assembly(data=None):
    if data is None:
        return None

    assembly = {
            'assembly_uuid':data.Assembly.assembly_uuid,
            'accession':data.Assembly.accession,
            'level':data.Assembly.level,
            'name':data.Assembly.name,
            'ucsc_name':data.Assembly.ucsc_name,
            'ensembl_name':data.Assembly.ensembl_name,
            'is_reference':data.Assembly.is_reference
    }
    return assembly


def create_taxon(data=None, alternative_names=[]):
    if data is None:
        return None

    taxon = {
        'alternative_names':alternative_names,
        'taxonomy_id':data.Organism.taxonomy_id,
        'scientific_name':data.Organism.scientific_name,
        'strain':data.Organism.strain,
    }
    return taxon


def create_organism(data=None):
    if data is None:
        return None

    organism = {
        'common_name':data.Organism.common_name,
        'strain':data.Organism.strain,
        'strain_type':data.Organism.strain_type,
        'scientific_name':data.Organism.scientific_name,
        'ensembl_name':data.Organism.biosample_id,
        'scientific_parlance_name':data.Organism.scientific_parlance_name,
        'organism_uuid':data.Organism.organism_uuid,
        'taxonomy_id':data.Organism.taxonomy_id,
        'species_taxonomy_id':data.Organism.species_taxonomy_id,
    }
    return organism


def create_attribute(data=None):
    if data is None:
        return None

    attribute = {
        'name':data.Attribute.name,
        'label':data.Attribute.label,
        'description':data.Attribute.description,
        'type':data.Attribute.type,
    }
    return attribute


def create_attributes_info(data=None):
    if data is None:
        return None

    # from EA-1105
    required_attributes = {
        "genebuild.method": "",
        "genebuild.method_display": "",
        "genebuild.last_geneset_update": "",
        "genebuild.provider_version": "",
        "genebuild.provider_name": "",
        "genebuild.provider_url": "",
        "genebuild.sample_gene": "",
        "genebuild.sample_location": "",
        "assembly.level": "",
        "assembly.date": "",
        "assembly.provider_name": "",
        "assembly.provider_url": "",
        "variation.sample_variant": ""
    }
    # set required_attributes values
    if type(data) is list and len(data) > 0:
        pass
    else:
        return None

    for attrib_data in data:
        attrib_name = attrib_data.name
        if attrib_name in list(required_attributes.keys()):
            required_attributes[attrib_name] = attrib_data.value

    return {
        'genebuild_method':required_attributes["genebuild.method"],
        'genebuild_method_display':required_attributes["genebuild.method_display"],
        'genebuild_last_geneset_update':required_attributes["genebuild.last_geneset_update"],
        'genebuild_provider_version':required_attributes["genebuild.provider_version"],
        'genebuild_provider_name':required_attributes["genebuild.provider_name"],
        'genebuild_provider_url':required_attributes["genebuild.provider_url"],
        'genebuild_sample_gene':required_attributes["genebuild.sample_gene"],
        'genebuild_sample_location':required_attributes["genebuild.sample_location"],
        'assembly_level':required_attributes["assembly.level"],
        'assembly_date':required_attributes["assembly.date"],
        'assembly_provider_name':required_attributes["assembly.provider_name"],
        'assembly_provider_url':required_attributes["assembly.provider_url"],
        'variation_sample_variant':required_attributes["variation.sample_variant"],
    }


def create_release(data=None):
    if data is None or data.EnsemblRelease is None:
        return None

    release = {
        'release_version':data.EnsemblRelease.version,
        'release_date':str(data.EnsemblRelease.release_date) if data.EnsemblRelease.release_date else "Unreleased",
        'release_label':data.EnsemblRelease.label,
        'release_type':data.EnsemblRelease.release_type,
        'is_current':data.EnsemblRelease.is_current,
        'site_name':data.EnsemblSite.name,
        'site_label':data.EnsemblSite.label,
        'site_uri':data.EnsemblSite.uri
    }
    return release


def create_genome_with_attributes_and_count(db_conn, genome, release_version):
    attrib_data_results = db_conn.fetch_genome_datasets(genome_uuid=genome.Genome.genome_uuid,
                                                        dataset_type_name="all",
                                                        release_version=release_version)

    logger.debug(f"Genome Datasets Retrieved: {attrib_data_results}")
    attribs = []
    if len(attrib_data_results) > 0:
        for dataset in attrib_data_results[0].datasets:
            attribs.extend(dataset.attributes)

    # fetch related assemblies count
    related_assemblies_count = db_conn.fetch_assemblies_count(genome.Organism.species_taxonomy_id)

    alternative_names = get_alternative_names(db_conn, genome.Organism.species_taxonomy_id)

    return create_genome(
        data=genome,
        attributes=attribs,
        count=related_assemblies_count,
        alternative_names=alternative_names,
        datasets=attrib_data_results[0].datasets
    )



def data_get_genome_by_uuid(db_conn, genome_uuid, release_version):
    if not genome_uuid:
        logger.warning("Missing or Empty Genome UUID field.")
        return None
    genome_results = db_conn.fetch_genomes(genome_uuid=genome_uuid, release_version=release_version)
    if len(genome_results) == 0:
        logger.error(f"No Genome/Release found: {genome_uuid}/{release_version}")
    else:
        if len(genome_results) > 1:
            logger.warning(f"Multiple results returned. {genome_results}")

        one_genome=genome_results[0]

        response_data = create_genome_with_attributes_and_count(
            db_conn=db_conn,
            genome=one_genome,
            release_version=release_version
        )
        return response_data
    return None



#def get_top_level_statistics(db_conn, organism_uuid):
#    if not organism_uuid:
#        logger.warning("Missing or Empty Organism UUID field.")
#        return None
#    # FIXME get best genome for organism and fetch from genome
#    genomes = db_conn.fetch_genomes(organism_uuid=organism_uuid)
#    #Todo fetch_genome returns duplicate genome uuids  if a genome assigned to multiple release and param allow_unreleased set to true
#    stats_results = db_conn.fetch_genome_datasets(genome_uuid=list({genome.Genome.genome_uuid for genome in genomes}),
#                                                  dataset_type_name="all")
#
#    if len(stats_results) > 0:
#        response_data = {
#            'organism_uuid': organism_uuid,
#            'stats_by_genome_uuid': stats_results
#        }
#        # logger.debug(f"Response data: \n{response_data}")
#        return response_data
#
#    logger.debug("No top level stats found.")
#    return None

def get_top_level_statistics_by_uuid(db_conn, genome_uuid):
    if not genome_uuid:
        logging.warning("Missing or Empty Genome UUID field.")
        return None

    stats_results = db_conn.fetch_genome_datasets(genome_uuid=genome_uuid, dataset_type_name="all")

    statistics = []
    # FIXME stats_results can contain multiple entries
    if len(stats_results) > 0:

        for dataset in stats_results[0].datasets:
            for attribute in dataset.attributes:
                statistics.append({
                    'name': attribute.name,
                    'label': attribute.label,
                    'statistic_type': attribute.type,
                    'statistic_value': attribute.value
                })

        statistics.sort(key=lambda x: x['name'])

        #logging.debug(f"Response data: \n{statistics}")
        return statistics

    logging.debug("No top level stats found.")
    return None

# OK
@router.get("/genome/{genome_uuid}/stats", name="statistics")
#@redis_cache("stats", arg_keys=["genome_uuid"])
async def get_metadata_statistics(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_uuid: str
):
    try:
        top_level_stats = get_top_level_statistics_by_uuid(adaptor, genome_uuid)
        genome_stats = GenomeStatistics(_raw_data=top_level_stats)
        logging.debug(genome_stats.model_dump())
        return responses.JSONResponse({"genome_stats": genome_stats.model_dump()})
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


def test_get_metadata_statistics():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/stats")
    assert response.status_code == 200
    assert response.json() == {
        "genome_stats":{
            "assembly_stats":{
                "contig_n50":54806562,
                "total_genome_length":3298912062,
                "total_coding_sequence_length":34493611,
                "total_gap_length":161611139,
                "spanned_gaps":663,
                "chromosomes":25,
                "toplevel_sequences":709,
                "component_sequences":36829,
                "gc_percentage":38.88
            },
            "coding_stats":{
                "coding_genes":20481,
                "average_genomic_span":67396.48,
                "average_sequence_length":None,
                "average_cds_length":1191.97,
                "shortest_gene_length":8,
                "longest_gene_length":2473539,
                "total_transcripts":170833,
                "coding_transcripts":111076,
                "transcripts_per_gene":8.34,
                "coding_transcripts_per_gene":5.42,
                "total_exons":1388435,
                "total_coding_exons":886243,
                "average_exon_length":250.15,
                "average_coding_exon_length":149.38,
                "average_exons_per_transcript":None,
                "average_coding_exons_per_coding_transcript":None,
                "total_introns":1217602,
                "average_intron_length":6172.48
            },
            "variation_stats":{
                "short_variants":1099106974,
                "structural_variants":None,
                "short_variants_with_phenotype_assertions":None,
                "short_variants_with_publications":None,
                "short_variants_frequency_studies":None,
                "structural_variants_with_phenotype_assertions":None
            },
            "non_coding_stats":{
                "non_coding_genes":25959,
                "small_non_coding_genes":4864,
                "long_non_coding_genes":18874,
                "misc_non_coding_genes":2221,
                "average_genomic_span":22981.34,
                "average_sequence_length":967.28,
                "shortest_gene_length":41,
                "longest_gene_length":1375317,
                "total_transcripts":64262,
                "transcripts_per_gene":2.48,
                "total_exons":224817,
                "average_exon_length":339.13,
                "average_exons_per_transcript":3.5,
                "total_introns":160555,
                "average_intron_length":14932.57
            },
            "pseudogene_stats":{
                "pseudogenes":15239,
                "average_genomic_span":3412.92,
                "average_sequence_length":725.47,
                "shortest_gene_length":23,
                "longest_gene_length":909387,
                "total_transcripts":16703,
                "transcripts_per_gene":1.1,
                "total_exons":35229,
                "average_exon_length":371.37,
                "average_exons_per_transcript":2.11,
                "total_introns":18526,
                "average_intron_length":4117.36
            },
            "homology_stats":{
                "coverage":91.6,
                "reference_species_name":"Pan troglodytes"
            },
            "regulation_stats":{
                "enhancers":246403,
                "promoters":35983,
                "ctcf_count":90891,
                "tfbs_count":30873,
                "open_chromatin_count":7541
            }
        }
    }

# OK
@router.get("/genome/{genome_uuid}/karyotype", name="karyotype")
# @redis_cache("karyotype", arg_keys=["genome_uuid"])
async def get_genome_karyotype(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_uuid: str
):
    try:
        top_level_regions = data_get_top_level_regions(adaptor, genome_uuid)

        # Temporary hack for e.coli and remov when the correct schema/data is available in metadata-database
        if genome_uuid == "a73351f7-93e7-11ec-a39d-005056b38ce3":
            for tlr in top_level_regions:
                tlr["is_circular"] = True
        karyotype_response = Karyotype(top_level_regions=top_level_regions)
        return responses.JSONResponse(
            karyotype_response.model_dump()["top_level_regions"]
        )
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


def data_get_top_level_regions(adaptor: GenomeAdaptor, genome_uuid: str):
    chromosomal_only=True
    top_level_regions = assembly_region_iterator(
        adaptor, genome_uuid, chromosomal_only
    )
    genome_top_level_regions = []
    for tlr in top_level_regions:
        genome_top_level_regions.append(tlr)

    # Sort the list of regions by two criteria:
    # 1. By "rank" if present, regions without a rank are considered to have the highest possible rank (so they go last)
    # 2. Then by "length", which is stored as a string, so we convert it to an integer for proper numeric sorting
    genome_top_level_regions.sort(
        key=lambda region: (
            # Use the value of "rank" if it exists, otherwise use infinity
            # This ensures regions without a rank are placed at the end of the list
            region.get("rank", float("inf")),

            # Convert the "length" from string to integer so numeric comparison works correctly
            # If "length" is missing, treat it as 0
            int(region.get("length", 0))
        )
    )
    return genome_top_level_regions


def assembly_region_iterator(db_conn, genome_uuid, chromosomal_only):
    if not genome_uuid:
        logger.warning("Missing or Empty Genome UUID field.")
        return

    assembly_sequence_results = db_conn.fetch_sequences(
        genome_uuid=genome_uuid,
        chromosomal_only=chromosomal_only,
    )
    for result in assembly_sequence_results:
        logger.debug(f"Processing assembly: {result.AssemblySequence.name}")
        yield create_assembly_region(result)

def create_assembly_region(data=None):
    if data is None:
        return None

    assembly_region = {
        'name':data.AssemblySequence.name,
        'rank':data.AssemblySequence.chromosome_rank,
        'md5':data.AssemblySequence.md5,
        'length':data.AssemblySequence.length,
        'sha512t24u':data.AssemblySequence.sha512t24u,
        'chromosomal':data.AssemblySequence.chromosomal
    }

    return assembly_region


def test_get_genome_karyotype():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/karyotype")
    assert response.status_code == 200
    assert response.json() == [
        {"name":"1", "type":"chromosome", "length":248956422, "is_circular":False},
        {"name":"2", "type":"chromosome", "length":242193529, "is_circular":False},
        {"name":"3", "type":"chromosome", "length":198295559, "is_circular":False},
        {"name":"4", "type":"chromosome", "length":190214555, "is_circular":False},
        {"name":"5", "type":"chromosome", "length":181538259, "is_circular":False},
        {"name":"6", "type":"chromosome", "length":170805979, "is_circular":False},
        {"name":"7", "type":"chromosome", "length":159345973, "is_circular":False},
        {"name":"8", "type":"chromosome", "length":145138636, "is_circular":False},
        {"name":"9", "type":"chromosome", "length":138394717, "is_circular":False},
        {"name":"10", "type":"chromosome", "length":133797422, "is_circular":False},
        {"name":"11", "type":"chromosome", "length":135086622, "is_circular":False},
        {"name":"12", "type":"chromosome", "length":133275309, "is_circular":False},
        {"name":"13", "type":"chromosome", "length":114364328, "is_circular":False},
        {"name":"14", "type":"chromosome", "length":107043718, "is_circular":False},
        {"name":"15", "type":"chromosome", "length":101991189, "is_circular":False},
        {"name":"16", "type":"chromosome", "length":90338345, "is_circular":False},
        {"name":"17", "type":"chromosome", "length":83257441, "is_circular":False},
        {"name":"18", "type":"chromosome", "length":80373285, "is_circular":False},
        {"name":"19", "type":"chromosome", "length":58617616, "is_circular":False},
        {"name":"20", "type":"chromosome", "length":64444167, "is_circular":False},
        {"name":"21", "type":"chromosome", "length":46709983, "is_circular":False},
        {"name":"22", "type":"chromosome", "length":50818468, "is_circular":False},
        {"name":"X", "type":"chromosome", "length":156040895, "is_circular":False},
        {"name":"Y", "type":"chromosome", "length":57227415, "is_circular":False},
        {"name":"MT", "type":"chromosome", "length":16569, "is_circular":False}
    ]


# OK
@router.get("/popular_species", name="popular_species")
#@redis_cache(key_prefix="popular_species")  # TTL defaults is 5 minutes
async def get_popular_species(
    adaptor: GenomeAdaptorDep,
    request: Request
):
    try:
        popular_species_dict = get_organisms_group_count(adaptor, None)
        popular_species = popular_species_dict["organisms_group_count"]
        popular_species_response = PopularSpeciesGroup(
            _base_url=request.headers["host"], popular_species=popular_species
        )
        return responses.JSONResponse(popular_species_response.model_dump())
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


def get_organisms_group_count(db_conn, release_label):
    count_result = db_conn.fetch_organisms_group_counts(release_label=release_label)
    response_data = create_organisms_group_count(count_result, release_label)
    # logger.debug(f"Response data: \n{response_data}")
    return response_data

def create_organisms_group_count(data, release_label):
    if data is None:
        return None

    organisms_list = []
    for organism in data:
        created_organism_group = {
            'species_taxonomy_id':organism[0],
            'common_name':organism[1],
            'scientific_name':organism[2],
            'order':organism[3],
            'count':organism[4],
        }
        organisms_list.append(created_organism_group)

    return {
        'organisms_group_count':organisms_list,
        'release_label':release_label
    }


def test_get_popular_species():
    response = client.get("/popular_species")
    assert response.status_code == 200
    assert response.json() == {
        "popular_species":
        [
            {
                "species_taxonomy_id":"9606",
                "name":"Human",
                "image":"//testserver/static/genome_images/9606.svg",
                "genomes_count":565},
            {
                "species_taxonomy_id":"10090",
                "name":"Mouse",
                "image":"//testserver/static/genome_images/10090.svg",
                "genomes_count":31},
            {
                "species_taxonomy_id":"7955",
                "name":"Zebrafish",
                "image":"//testserver/static/genome_images/7955.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"4565",
                "name":"Bread wheat",
                "image":"//testserver/static/genome_images/4565.svg",
                "genomes_count":20},
            {
                "species_taxonomy_id":"4530",
                "name":"Japanese rice",
                "image":"//testserver/static/genome_images/4530.svg",
                "genomes_count":21},
            {
                "species_taxonomy_id":"3702",
                "name":"Thale-cress",
                "image":"//testserver/static/genome_images/3702.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"9913",
                "name":"Cattle",
                "image":"//testserver/static/genome_images/9913.svg",
                "genomes_count":5},
            {
                "species_taxonomy_id":"10116",
                "name":"Norway rat",
                "image":"//testserver/static/genome_images/10116.svg",
                "genomes_count":6},
            {
                "species_taxonomy_id":"9823",
                "name":"Pig",
                "image":"//testserver/static/genome_images/9823.svg",
                "genomes_count":29},
            {
                "species_taxonomy_id":"4577",
                "name":"Maize",
                "image":"//testserver/static/genome_images/4577.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"9031",
                "name":"Chicken",
                "image":"//testserver/static/genome_images/9031.svg",
                "genomes_count":5},
            {
                "species_taxonomy_id":"9612",
                "name":"Dog",
                "image":"//testserver/static/genome_images/9612.svg",
                "genomes_count":7},
            {
                "species_taxonomy_id":"4513",
                "name":"Domesticated barley",
                "image":"//testserver/static/genome_images/4513.svg",
                "genomes_count":69},
            {
                "species_taxonomy_id":"7227",
                "name":"Fruit fly",
                "image":"//testserver/static/genome_images/7227.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"8090",
                "name":"Japanese medaka",
                "image":"//testserver/static/genome_images/8090.svg",
                "genomes_count":15},
            {
                "species_taxonomy_id":"9940",
                "name":"Sheep",
                "image":"//testserver/static/genome_images/9940.svg",
                "genomes_count":22},
            {
                "species_taxonomy_id":"29760",
                "name":"Wine grape",
                "image":"//testserver/static/genome_images/29760.svg",
                "genomes_count":2},
            {
                "species_taxonomy_id":"4081",
                "name":"Tomato",
                "image":"//testserver/static/genome_images/4081.svg",
                "genomes_count":2},
            {
                "species_taxonomy_id":"9796",
                "name":"Horse",
                "image":"//testserver/static/genome_images/9796.svg",
                "genomes_count":3},
            {
                "species_taxonomy_id":"3708",
                "name":"Oilseed rape",
                "image":"//testserver/static/genome_images/3708.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"4113",
                "name":"Potato",
                "image":"//testserver/static/genome_images/4113.svg",
                "genomes_count":2},
            {
                "species_taxonomy_id":"9986",
                "name":"Rabbit",
                "image":"//testserver/static/genome_images/9986.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"4932",
                "name":"Baker's yeast",
                "image":"//testserver/static/genome_images/4932.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"6239",
                "name":"Roundworm",
                "image":"//testserver/static/genome_images/6239.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"9685",
                "name":"Domestic cat",
                "image":"//testserver/static/genome_images/9685.svg",
                "genomes_count":3},
            {
                "species_taxonomy_id":"9544",
                "name":"Macaque",
                "image":"//testserver/static/genome_images/9544.svg",
                "genomes_count":2},
            {
                "species_taxonomy_id":"7994",
                "name":"Mexican tetra",
                "image":"//testserver/static/genome_images/7994.svg",
                "genomes_count":6},
            {
                "species_taxonomy_id":"4571",
                "name":"Durum wheat",
                "image":"//testserver/static/genome_images/4571.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"9598",
                "name":"Chimpanzee",
                "image":"//testserver/static/genome_images/9598.svg",
                "genomes_count":3},
            {
                "species_taxonomy_id":"8128",
                "name":"Nile tilapia",
                "image":"//testserver/static/genome_images/8128.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"9925",
                "name":"Goat",
                "image":"//testserver/static/genome_images/9925.svg",
                "genomes_count":4},
            {
                "species_taxonomy_id":"3712",
                "name":"Wild cabbage",
                "image":"//testserver/static/genome_images/3712.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"8364",
                "name":"Tropical clawed frog",
                "image":"//testserver/static/genome_images/8364.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"3847",
                "name":"Soybeans",
                "image":"//testserver/static/genome_images/3847.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"10029",
                "name":"Chinese hamster",
                "image":"//testserver/static/genome_images/10029.svg",
                "genomes_count":3},
            {
                "species_taxonomy_id":"3880",
                "name":"Barrel medic",
                "image":"//testserver/static/genome_images/3880.svg",
                "genomes_count":2},
            {
                "species_taxonomy_id":"3711",
                "name":"Field mustard",
                "image":"//testserver/static/genome_images/3711.svg",
                "genomes_count":3},
            {
                "species_taxonomy_id":"4558",
                "name":"Sorghum",
                "image":"//testserver/static/genome_images/4558.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"8030",
                "name":"Atlantic salmon",
                "image":"//testserver/static/genome_images/8030.svg",
                "genomes_count":4},
            {
                "species_taxonomy_id":"37682",
                "name":"Tausch's goatgrass",
                "image":"//testserver/static/genome_images/37682.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"562",
                "name":"Escherichia coli K-12",
                "image":"//testserver/static/genome_images/562.svg",
                "genomes_count":1},
            {
                "species_taxonomy_id":"5833",
                "name":"Malaria parasite",
                "image":"//testserver/static/genome_images/5833.svg",
                "genomes_count":2
            }
        ]
    }


# OK
@router.get("/validate_location", name="validate_location")
def validate_region(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_id: str,
    location: str
):
    try:
        rgv = RegionValidation(genome_uuid=genome_id, location_input=location)
        rgv.validate_region(adaptor)
        return responses.JSONResponse(rgv.model_dump())
    except Exception as e:
        logging.error(e)
        return response_error_handler({"status": 500})


def test_validate_region():
    response = client.get("/validate_location?genome_id=a7335667-93e7-11ec-a39d-005056b38ce3&location=8:26291508-26372680")
    assert response.status_code == 200
    assert response.json() == {
        "region":{
            "error_code":None,
            "error_message":None,
            "region_name":"8",
            "is_valid":True
        },
        "start":{
            "error_code":None,
            "error_message":None,
            "value":26291508,
            "is_valid":True
        },
        "end":{
            "error_code":None,
            "error_message":None,
            "value":26372680,
            "is_valid":True
        },
        "location":"8:26291508-26372680"
    }



# OK
@router.get("/genome/{genome_id}/example_objects", name="example_objects")
#@redis_cache("example_objects", arg_keys=["genome_id"])
async def example_objects(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_id: str
):
    try:
        attributes_info = get_attributes_by_genome_uuid(adaptor, genome_id, None)
        if attributes_info:
            example_objects = ExampleObjectList(
                example_objects=attributes_info["attributes_info"]
            )
            response_data = responses.JSONResponse(
                example_objects.model_dump()["example_objects"]
            )
        else:
            return response_error_handler({
                "status": 404,
                "details": f"Could not find example objects for {genome_id}"
            })
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


def get_attributes_by_genome_uuid(db_conn, genome_uuid, release_version):
    if not genome_uuid:
        logger.warning("Missing or Empty Genome UUID field.")
        return None

    attrib_data_results = db_conn.fetch_genome_datasets(genome_uuid=genome_uuid,
                                                        dataset_type_name="all",
                                                        release_version=release_version)

    logger.debug(f"Genome Datasets Retrieved: {attrib_data_results}")

    if len(attrib_data_results) == 0:
        logger.error(f"No Attributes were found: {genome_uuid}/{release_version}")
    else:
        if len(attrib_data_results) > 0:
            attribs = []
            for dataset in attrib_data_results[0].datasets:
                attribs.extend(dataset.attributes)

            attributes_info = create_attributes_info(attribs)
            return {
                'genome_uuid':genome_uuid,
                'attributes_info':attributes_info
            }
    return None


def test_example_objects():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/example_objects")
    assert response.status_code == 200
    assert response.json() == [{"type":"gene","id":"ENSG00000221914"},{"type":"location","id":"8:26291508-26372680"},{"type":"variant","id":"1:230710048:rs699"}]



# OK
@router.get("/genome/{genome_uuid}/details", name="genome_details")
#@redis_cache("details", arg_keys=["genome_uuid"])
async def get_genome_details(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_uuid: str):
    try:
        genome_details_dict = data_get_genome_by_uuid(adaptor, genome_uuid, None)

        if genome_details_dict:
            genome_details = GenomeDetails(**genome_details_dict)
            response_data = responses.JSONResponse(genome_details.model_dump(
                exclude={
                    "release": {"is_current"},
                }
            ))
        else:
            return response_error_handler({
                "status": 404,
                "details": f"Could not find details for {genome_uuid}"
            })
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data



def test_get_genome_details():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/details")
    assert response.status_code == 200
    assert response.json() == {
        "genome_id":"a7335667-93e7-11ec-a39d-005056b38ce3",
        "genome_tag":None,
        "common_name":"Human",
        "scientific_name":"Homo sapiens",
        "species_taxonomy_id":"9606",
        "type":None,
        "is_reference":True,
        "assembly":{
            "accession_id":"GCA_000001405.29",
            "name":"GRCh38.p14",
            "url":"https://identifiers.org/insdc.gca/GCA_000001405.29"
        },
        "release":{
            "name":"2025-02",
            "type":"integrated"
        },
        "taxonomy_id":"9606",
        "assembly_provider": {
            'name': 'Genome Reference Consortium',
            'url': 'https://www.ncbi.nlm.nih.gov/grc',
        },
        "assembly_level":"chromosome",
        "assembly_date":"2013-12",
        "annotation_provider":{
            "name":"Ensembl",
            "url":"https://www.ensembl.org"
        },
        "annotation_method":"Ensembl Genebuild",
        "annotation_version":"44",
        "annotation_date":"2023-03",
        "number_of_genomes_in_group":565
    }



# OK
@router.get("/genome/{genome_uuid}/ftplinks", name="genome_ftplinks")
#@redis_cache("ftplinks", arg_keys=["genome_uuid"])
async def get_genome_ftplinks(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_uuid: str
):
    try:
        ftplinks_dict = get_ftp_links(
            adaptor,
            genome_uuid,
            "all",
            None
        )

        # This is temporary solution to hide regulation ftp links
        # It should be removed once the ftp links for regulation is fixed
        ftplinks_no_regulation = {}
        ftplinks_no_regulation["links"] = [
            link
            for link in sorted(ftplinks_dict["links"], key=lambda d: d['dataset_type'])
            if link["dataset_type"] != "regulation"
        ]

        ftplinks = FTPLinks(**ftplinks_no_regulation)
        return responses.JSONResponse(ftplinks.model_dump().get("links", []))
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})



def get_ftp_links(db_conn, genome_uuid, dataset_type, release_version):
    # Request is sending an empty string '' instead of None when
    # an input parameter is not supplied by the user
    if not genome_uuid:
        logger.warning("Missing or Empty Genome UUID field.")
        return None
    if not dataset_type:
        dataset_type = 'all'
    if not release_version:
        release_version = None

    # Find the Genome
    with db_conn.metadata_db.session_scope() as session:
        genome = session.query(Genome).filter(Genome.genome_uuid == genome_uuid).first()

        # Return empty links if Genome is not found
        if genome is None:
            logger.debug("No Genome found.")
            return None

        # Find the links for the given dataset.
        # Find the links for the given dataset.
        # Note: release_version filtration is not implemented in the API yet
        try:
            links = db_conn.get_public_path(
                genome_uuid=genome_uuid,
                dataset_type=dataset_type
            )
        except (ValueError, RuntimeError) as error:
            # log the errors to error log and return empty list of links
            logger.error(f"Error fetching links: {error}")
            return None

    if len(links) > 0:
        response_data = create_paths(data=links)
        # logger.debug(f"Response data: \n{response_data}")
        return response_data

    logger.debug("No Genome found.")
    return None


def create_paths(data=None):
    if data is None:
        return {
            'links':[]
        }

    ftp_links_list = []
    for ftp_link in data:
        created_ftp_link = {
            'dataset_type':ftp_link["dataset_type"],
            'path':ftp_link["path"]
        }
        ftp_links_list.append(created_ftp_link)

    return {
        'links':ftp_links_list
    }


def test_get_genome_ftplinks():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/ftplinks")
    assert response.status_code == 200
    assert response.json() == [
        {
            "dataset":"assembly",
            "url":"https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/genome"
        },
        {
            "dataset":"genebuild",
            "url":"https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/ensembl/geneset/2023_03"
        },
        {
            "dataset":"homologies",
            "url":"https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/ensembl/homology/2023_03"
        },
        {
            "dataset":"variation",
            "url":"https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/ensembl/variation/2023_03"
        }
    ]


# OK
@router.get("/genome/{genome_id_or_slug}/explain", name="genome_explain")
#@redis_cache(key_prefix="explain", arg_keys=['genome_id_or_slug'])
async def explain_genome(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_id_or_slug: str
):
    try:
        genome_details_dict = get_brief_genome_details_by_uuid(adaptor, genome_id_or_slug, None)
        if genome_details_dict:
            genome_details = BriefGenomeDetails(**genome_details_dict)
            response_dict = genome_details.model_dump(
                include={
                    "genome_id": True,
                    "genome_tag": True,
                    "scientific_name": True,
                    "species_taxonomy_id": True,
                    "common_name": True,
                    "is_reference": True,
                    "assembly": {"name", "accession_id"},
                    "release": {"name", "type"},
                    "type": True,
                    "latest_genome": True,
                }
            )
            response_data = responses.JSONResponse(response_dict, status_code=200)
        else:
            return response_error_handler({
                "status": 404,
                "details": f"Could not explain {genome_id_or_slug}"
            })
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})
    return response_data


def get_brief_genome_details_by_uuid(db_conn, genome_uuid_or_tag, release_version):
    """
    Fetch brief genome details by UUID or tag and release version.

    Args:
        db_conn: Database connection object.
        genome_uuid_or_tag: Genome UUID or tag.
        release_version: Release version to fetch.

    Returns:
        A dictionary containing brief genome details.
    """
    if not genome_uuid_or_tag:
        logger.warning("Missing or Empty Genome UUID field.")
        return None

    # If genome_uuid_or_tag is not a valid UUID, assume it's a tag and fetch genome_uuid
    if not is_valid_uuid(genome_uuid_or_tag):
        logger.debug(f"Invalid genome_uuid {genome_uuid_or_tag}, assuming it's a tag and using it to fetch genome_uuid")
        # For tag (URL name), we only care about the latest integrated release.
        # For archives, we will need to keep in mind the combination of release and tag
        # that will take the user to the archived version of the genome.
        genome_results = db_conn.fetch_genomes(
            genome_tag=genome_uuid_or_tag,
            # release_type="integrated", #  Add this once we have tags linked only to integrated releases
            release_version=release_version
        )
    else:
        genome_uuid = genome_uuid_or_tag
        genome_results = db_conn.fetch_genomes(genome_uuid=genome_uuid, release_version=release_version)

    if not genome_results:
        logger.error(f"No Genome/Release found: {genome_uuid_or_tag}/{release_version}")
        return None

    if len(genome_results) > 1:
        logger.warning(f"Multiple results found for Genome UUID/Release version: {genome_uuid_or_tag}/{release_version}")
        # means that this genome is released in both a partial and integrated release
        # we get the integrated release specifically since it's the one we are interested in
        genome_results = [res for res in genome_results if res.EnsemblRelease.release_type == "integrated"]

    # Get the current (requested) genome
    current_genome = genome_results[0]
    assembly_name = current_genome.Assembly.name
    # Fetch all genomes with the same assembly name, sorted by release date
    all_genomes_with_same_assembly = db_conn.fetch_genomes(assembly_name=assembly_name)

    # Find the genome with the most recent release date
    latest_genome = None
    if all_genomes_with_same_assembly:
        # First genome should be the latest due to ordering in fetch_genomes
        if all_genomes_with_same_assembly[0].Genome.genome_uuid != current_genome.Genome.genome_uuid:
            latest_genome = all_genomes_with_same_assembly[0]
            logger.debug(f"Found newer genome: {latest_genome.Genome.genome_uuid}")

    # Return the requested genome together with the latest genome details (or None if current is latest)
    return create_brief_genome_details(current_genome, latest_genome)


def create_brief_genome_details(data=None, latest_genome=None):
    if data is None:
        return None

    # current genome
    assembly = create_assembly(data)
    taxon = create_taxon(data)
    organism = create_organism(data)
    release = create_release(data)

    # add latest_genome details
    latest_genome_data = None
    if latest_genome and latest_genome.Genome.genome_uuid != data.Genome.genome_uuid:
        latest_genome_data = create_brief_genome_details(latest_genome, None)

    brief_genome_details = {
        'genome_uuid':data.Genome.genome_uuid,
        'created':str(data.Genome.created),
        'assembly':assembly,
        'taxon':taxon,
        'organism':organism,
        'release':release,
        'latest_genome':latest_genome_data
    }
    return brief_genome_details


# OK
@router.get("/genome/{genome_uuid}/checksum/{region_name}", name="region_checksum")
async def get_region_checksum(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_uuid: str,
    region_name: str
):
    try:
        region_checksum_dict = genome_assembly_sequence_region(
            db_conn=adaptor,
            genome_uuid=genome_uuid,
            sequence_region_name=region_name
        )
        region_checksum = Checksum(**region_checksum_dict)
        return responses.PlainTextResponse(region_checksum.md5)
    except ValidationError as e:
        error_type = e.errors()[0]["type"]
        if error_type.index("missing") == 0:
            return response_error_handler({"status": 404})
    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


def genome_assembly_sequence_region(db_conn, genome_uuid, sequence_region_name):
    if not genome_uuid or not sequence_region_name:
        logger.warning("Missing or Empty Genome UUID or Sequence region name field.")
        return None

    assembly_sequence_results = db_conn.fetch_sequences(
        genome_uuid=genome_uuid,
        assembly_sequence_name=sequence_region_name
    )
    if len(assembly_sequence_results) == 0:
        logger.error(f"Assembly sequence not found for {genome_uuid}/{sequence_region_name}")
    else:
        if len(assembly_sequence_results) > 1:
            logger.warning(f"Multiple results returned for {genome_uuid}/{sequence_region_name}")
        response_data = create_genome_assembly_sequence_region(assembly_sequence_results[0])
        return response_data
    return None


def create_genome_assembly_sequence_region(data=None):
    if data is None:
        return None

    genome_assembly_sequence_region = {
        'name':data.AssemblySequence.name,
        'md5':data.AssemblySequence.md5,
        'length':data.AssemblySequence.length,
        'sha512t24u':data.AssemblySequence.sha512t24u,
        'chromosomal':data.AssemblySequence.chromosomal
    }

    return genome_assembly_sequence_region


def test_get_region_checksum():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/checksum/1")
    assert response.status_code == 200
    assert response.content.decode("utf-8") == "2648ae1bacce4ec4b6cf337dcae37816"


# OK
@router.get(
    "/genome/{genome_uuid}/dataset/{dataset_type}/attributes", name="dataset_attributes"
)
async def get_genome_dataset_attributes(
    adaptor: GenomeAdaptorDep,
    request: Request,
    genome_uuid: str,
    dataset_type: str,
    attribute_names: Annotated[list[str] | None, Query()] = None,
):
    try:
        dataset_attributes = get_dataset_attributes(
                adaptor,
                genome_uuid,
                dataset_type,
                attribute_names
            )
        if len(dataset_attributes.get("attributes",[])) == 0:
            return responses.JSONResponse(
                {
                    "message": f"Could not find details for genome {genome_uuid} and dataset {dataset_type}."
                },
                status_code=404,
            )
        dataset_attributes_object = DatasetAttributes(**dataset_attributes)
        response_data = responses.JSONResponse(
            dataset_attributes_object.dict(), status_code=200
        )
        return response_data

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


def get_dataset_attributes(
    adaptor: GenomeAdaptor,
    genome_uuid: str,
    dataset_type: str,
    attribute_names: list
):
    release_version = None
    latest_only = False
    return get_attributes_values_by_uuid(
        adaptor,
        genome_uuid,
        dataset_type,
        release_version,
        attribute_names,
        latest_only
    )



def get_attributes_values_by_uuid(db_conn, genome_uuid, dataset_type, release_version, attribute_names, latest_only):
    """
    Retrieve attribute values for a given genome UUID from the database.

    This function fetches genome datasets based on the provided genome UUID, dataset type, and release version.
    If a single dataset result is found, it creates and returns the attribute values. If no or multiple datasets
    are found, appropriate warnings or debug messages are logged.

    Args:
        db_conn: Database connection object.
        genome_uuid (str): The UUID of the genome to fetch data for. Must not be empty.
        dataset_type (str): The type of dataset to retrieve.
        release_version (str): The release version of the dataset to retrieve.
        attribute_names (list): A list of attribute names to filter the results by.
        latest_only (bool): Whether to fetch the latest dataset or not (default is `False`).

    Returns:
        object: A response object containing the attribute values. If no valid dataset is found,
                an empty attribute value object is returned.
    """
    if not genome_uuid:
        logger.warning("Missing or Empty Genome UUID field.")
        return None

    genome_datasets_results = db_conn.fetch_genome_datasets(
        genome_uuid=genome_uuid,
        dataset_type_name=dataset_type,
        release_version=release_version
    )

    if len(genome_datasets_results) > 1:
        logger.debug("Multiple results returned.")
        # if we get more than one genome, it means it's attached to both partial and integrated releases
        # we pick the integrated genome because it's the one taking precedence
        genome_datasets_results = [gd for gd in genome_datasets_results if gd.release.release_type == 'integrated']

    if len(genome_datasets_results) == 1:
        response_data = create_attribute_value(
            data=genome_datasets_results,
            # There is no point in filtering by attribute_names in the API because it returns the whole dataset object
            # which will contain all the attributes (we should be altering them from within the API)
            attribute_names=attribute_names,
            latest_only=latest_only
        )
        logger.debug(f"Response data: \n{response_data}")
        return response_data
    else:
        logger.debug("Genome not found.")

    logger.debug("No attribute values were found.")
    return None



def create_attribute_value(data=None, attribute_names=None, latest_only=False):
    """
    Creates a DatasetAttributesValues message from the provided data.

    If no data is provided, returns an empty DatasetAttributeValue message with an empty attributes list.

    Args:
        data (optional): A list of objects containing dataset attributes.
            The expected structure is that `data` is a list containing an object with a `datasets` attribute,
            which is a list containing an object with an `attributes` attribute. The `attributes` attribute
            is a list of objects each having `name` and `value` attributes.
            it's many nested objects, and we need to go deep in the rabit hole to fetch the data we need
            The nested objects look something like this:
            [GenomeDatasetsListItem]
                [GenomeDatasetItem]
                    [DatasetAttributeItem] <- this is the attributes list we want to extract
                    Dataset
                    GenomeDataset
                Genome
                EnsemblRelease

        attribute_names (optional): A List of attributes names to filter by
        latest_only (optional): Whether to fetch the latest dataset or not (default is `False`)

    Returns:
        ensembl_metadata_pb2.DatasetAttributesValues: A message containing a list of DatasetAttributeValue
        messages, each corresponding to the attributes from the input data.
    """
    def add_attributes(ds_item, attributes_list, dataset_version, dataset_uuid, attribute_names, dataset_type):
        """
        Adds attributes from a dataset item to the attributes list.
        """
        for attrib in ds_item.attributes:
            # (1) if attribute_names is not provided,
            # (2) Or attribute_name from the DB is in the provided attribute_names
            # append it to the list of the returned result
            # if (1) is true, we will be fetching all the attributes
            # if (2) is true, we will be fetching the requested attributes only
            if not attribute_names or attrib.name in attribute_names:
                created_attribute = {
                    'attribute_name':attrib.name,
                    'attribute_value':attrib.value,
                    'dataset_version':dataset_version,
                    'dataset_uuid':dataset_uuid,
                    'dataset_type':dataset_type
                }
                attributes_list.append(created_attribute)

    if data is None:
        return {
            'attributes':[]
        }

    attributes_list = []
    # we can have more than one dataset
    for ds_item in data[0].datasets:
        # that we can distinguish by version or dataset_uuid
        dataset_version = ds_item.dataset.version
        dataset_uuid = ds_item.dataset.dataset_uuid
        dataset_type = ds_item.dataset.dataset_type.name

        # get the latest if latest_only is True
        if latest_only:
            if ds_item.release.is_current:
                add_attributes(ds_item, attributes_list, dataset_version, dataset_uuid, attribute_names, dataset_type)
        else:
            add_attributes(ds_item, attributes_list, dataset_version, dataset_uuid, attribute_names, dataset_type)

    return {
        'attributes':attributes_list,
        'release_version':data[0].release.version
    }


def test_get_genome_dataset_attributes():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/dataset/genebuild/attributes")
    assert response.status_code == 200
    assert response.json() == {
    "attributes":[
        {
            "name":"genebuild.stats.average_cds_length",
            "value":"1191.97",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.average_coding_exons_per_coding_transcript",
            "value":"7.98",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.average_coding_exons_per_transcript",
            "value":"8.13",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.average_coding_exon_length",
            "value":"149.38",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.average_exon_length",
            "value":"250.15",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.average_genomic_span",
            "value":"67396.48",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.average_intron_length",
            "value":"6172.48",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.average_sequence_legth",
            "value":"3566.92",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.coding_genes",
            "value":"20481",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.coding_transcripts",
            "value":"111076",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.coding_transcripts_per_gene",
            "value":"5.42",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.initial_release_date",
            "value":"2014-07",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.last_geneset_update",
            "value":"2023-03",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.level",
            "value":"toplevel",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.longest_gene_length",
            "value":"2473539",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.method",
            "value":"full_genebuild",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.method_display",
            "value":"Ensembl Genebuild",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_average_exons_per_transcript",
            "value":"3.50",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_average_exon_length",
            "value":"339.13",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_average_genomic_span",
            "value":"22981.34",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_average_sequence_length",
            "value":"967.28",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_longest_gene_length",
            "value":"1375317",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_long_non_coding_genes",
            "value":"18874",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_misc_non_coding_genes",
            "value":"2221",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_non_coding_genes",
            "value":"25959",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_shortest_gene_length",
            "value":"41",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_small_non_coding_genes",
            "value":"4864",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_total_introns",
            "value":"160555",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_total_transcripts",
            "value":"64262",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_transcripts_per_gene",
            "value":"2.48",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_average_exons_per_transcript",
            "value":"2.11",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_average_exon_length",
            "value":"371.37",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_average_genomic_span",
            "value":"3412.92",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_average_intron_length",
            "value":"4117.36",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_average_sequence_length",
            "value":"725.47",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_longest_gene_length",
            "value":"909387",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_pseudogenes",
            "value":"15239",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_shortest_gene_length",
            "value":"23",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_total_exons",
            "value":"35229",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_total_introns",
            "value":"18526",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_total_transcripts",
            "value":"16703",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.ps_transcripts_per_gene",
            "value":"1.10",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.shortest_gene_length",
            "value":"8",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.start_date",
            "value":"2014-01-Ensembl",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.total_coding_exons",
            "value":"886243",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.total_exons",
            "value":"1388435",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.total_introns",
            "value":"1217602",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.total_transcripts",
            "value":"170833",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.transcripts_per_gene",
            "value":"8.34",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.version",
            "value":"GENCODE44",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.sample_gene",
            "value":"ENSG00000221914",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.sample_location",
            "value":"8:26291508-26372680",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.id",
            "value":"39",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_average_intron_length",
            "value":"14932.57",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.havana_datafreeze_date",
            "value":"19-12-2022",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.provider_name",
            "value":"Ensembl",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.provider_url",
            "value":"https://www.ensembl.org",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.annotation_source",
            "value":"ensembl",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.stats.nc_total_exons",
            "value":"224817",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.provider_version",
            "value":"44",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"vep.faa_location",
            "value":"Homo_sapiens/GCA_000001405.29/vep/genome/softmasked.fa.bgz",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"vep.gff_location",
            "value":"Homo_sapiens/GCA_000001405.29/vep/ensembl/geneset/2023_03/genes.gff3.bgz",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_version",
            "value":"5.4.7",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_dataset",
            "value":"euarchontoglires_odb10",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco",
            "value":"C:99.7%[S:98.1%,D:1.6%],F:0.0%,M:0.3%,n:12692",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_mode",
            "value":"protein",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_completeness",
            "value":"12652",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_single_copy",
            "value":"12445",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_duplicated",
            "value":"207",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_fragmented",
            "value":"2",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_missing",
            "value":"38",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.busco_total",
            "value":"12692",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"},
        {
            "name":"genebuild.team_responsible",
            "value":"Genebuild",
            "version":"GENCODE44",
            "uuid":"949defef-c4d2-4ab1-8a73-f41d2b3c7719",
            "type":"genebuild"}
    ],
    "release_version":1.0
}


# OK
@router.get("/genomeid")
async def get_genome_by_keyword(
    adaptor: GenomeAdaptorDep,
    request: Request,
    assembly_accession_id: str
):
    try:
        genome_response = get_genomes_by_specific_keyword_iterator(
            db_conn=adaptor,
            tolid=None,
            assembly_accession_id=assembly_accession_id,
            assembly_name=None,
            ensembl_name=None,
            common_name=None,
            scientific_name=None,
            scientific_parlance_name=None,
            species_taxonomy_id=None,
            release_version=None
        )
        latest_genome_by_keyword_object = GenomeByKeyword()
        for arr in genome_response:
            genome_by_keyword_object = GenomeByKeyword(**arr)
            if (genome_by_keyword_object.release_version > latest_genome_by_keyword_object.release_version):
                latest_genome_by_keyword_object = genome_by_keyword_object
        if (latest_genome_by_keyword_object.genome_uuid):
            return responses.JSONResponse(latest_genome_by_keyword_object.model_dump())
        else:
            logging.error(f"Assembly accession id {assembly_accession_id} not found")
            return response_error_handler({"status": 404})

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


def get_genomes_by_specific_keyword_iterator(
    db_conn, tolid, assembly_accession_id, assembly_name, ensembl_name,
    common_name, scientific_name, scientific_parlance_name, species_taxonomy_id,
    release_version=None
):
    if (not (tolid or assembly_accession_id or assembly_name or ensembl_name or
            common_name or scientific_name or scientific_parlance_name or species_taxonomy_id)):
        logger.warning("Missing required field")
        return None

    try:
        genome_results = db_conn.fetch_genome_by_specific_keyword(
            tolid, assembly_accession_id, assembly_name, ensembl_name,
            common_name, scientific_name, scientific_parlance_name,
            species_taxonomy_id, release_version
        )

        if len(genome_results) > 0:
            # Create an empty list to store the genomes list
            genomes_list = []
            # sort genomes based on the `assembly_accession` field since we are going to group by it
            genome_results.sort(key=lambda r: r.Assembly.accession)
            # Group `genome_results` based on the `assembly_accession` field
            for _, genome_release_group in itertools.groupby(genome_results, lambda r: r.Assembly.accession):
                # Sort the genomes in each group based on the `genome_uuid` field to prepare for grouping
                sorted_genomes = sorted(genome_release_group, key=lambda g: g.Genome.genome_uuid)
                # group by genome uuid incase of partial and integrated releases
                for _, genome_uuid_group in itertools.groupby(sorted_genomes, lambda g: g.Genome.genome_uuid):
                    genome_uuid_group = list(genome_uuid_group)
                    if len(genome_uuid_group) > 1:
                        # sort by release date descending. The last code checked if EnsemblRelease exists. If it doesn't it uses a default date and not genome uuid
                        sorted_genome_uuid_group = sorted(
                            genome_uuid_group,
                            key=lambda g: getattr(g.EnsemblRelease, 'release_date', datetime.strptime('1900-01-01', '%Y-%m-%d')) if g.EnsemblRelease else datetime.strptime('1900-01-01', '%Y-%m-%d'),
                            reverse=True
                        )
                        # check for integrated release in group
                        integrated_genome = [
                            g for g in sorted_genome_uuid_group
                            if g.EnsemblRelease and getattr(g.EnsemblRelease, 'release_type', None) == 'integrated'
                        ]
                        if len(integrated_genome) > 0:
                            genomes_list.append(integrated_genome[0])

                        # if no integrated release, just take the first one, which is the most recent partial release
                        else:
                            genomes_list.append(sorted_genome_uuid_group[0])
                    # if only one genome in the group, just add it to the list
                    else:
                        genomes_list.append(list(genome_uuid_group)[0])

            for genome_row in genomes_list:
                yield create_genome(data=genome_row)

    except Exception as e:
        logger.error(f"Error fetching genomes: {e}")
        return None

    logger.debug("No genomes were found.")
    return None


def test_get_genome_by_keyword():
    response = client.get("/genomeid?assembly_accession_id=GCA_000001405.29")
    assert response.status_code == 200
    assert response.json() == {
        "genome_uuid":"be73075e-0633-471d-b7c8-4f8ca7752a04",
        "release_version":115.3,
        "genome_tag":""
    }


# OK
@router.get("/genome/{genome_uuid}/vep/file_paths")
async def get_vep_file_paths(
    adaptor: VepAdaptorDep,
    request: Request,
    genome_uuid: str,
):
    try:
        vep_file_paths = get_vep_paths_by_uuid(adaptor, genome_uuid)
        if len(vep_file_paths) == 0:
            return responses.JSONResponse(
                {
                    "message": f"Could not find VEP file paths for genome {genome_uuid}."
                },
                status_code=404,
            )

        vep_file_paths_object = VepFilePaths(**vep_file_paths)
        return responses.JSONResponse(
            vep_file_paths_object.dict(), status_code=200
        )

    except Exception as ex:
        logging.error(ex)
        return response_error_handler({"status": 500})


def get_vep_paths_by_uuid(db_conn: VepAdaptor, genome_uuid: str):
    if not genome_uuid:
        logger.warning("Missing or Empty Genome UUID field.")
        return None

    try:
        vep_paths = db_conn.fetch_vep_locations(genome_uuid=genome_uuid)
        if vep_paths:
            return vep_paths
    except (ValueError, RuntimeError) as error:
        logger.error(error)

    return None


def test_get_vep_file_paths():
    response = client.get("/genome/2b5fb047-5992-4dfb-b2fa-1fb4e18d1abb/vep/file_paths")
    assert response.status_code == 200
    assert response.json() == {
        "faa_location":"Homo_sapiens/GCA_000001405.29/vep/genome/softmasked.fa.bgz",
        "gff_location":"Homo_sapiens/GCA_000001405.29/vep/ensembl/geneset/2024_11/genes.gff3.bgz"
    }


# OK
@router.get("/releases", name="get_releases")
#@redis_cache("releases")
async def get_releases(
	adaptor: ReleaseAdaptorDep,
    request: Request,
    release_name: list[str] = Query(None, description="Filter by release name(s)"),
    current_only: bool = Query(False, description="Only current releases")
):
    try:
        releases_stream = release_iterator(
			adaptor,
			site_name=None,
            release_label=release_name,
            current_only=current_only
        )

        releases_list = []
        for release_msg in releases_stream:
            release = Release(**release_msg)
            releases_list.append(release)

        if releases_list:
            # Serialize each release into the desired format
            response_list = []
            for release in releases_list:
                response_dict = release.model_dump(
                    include={
                        "name": True,
                        "type": True,
                        "is_current": True,
                    }
                )
                response_list.append(response_dict)
            response_data = responses.JSONResponse(response_list, status_code=200)
        else:
            return response_error_handler({
                "status": 404,
                "details": "No releases found matching criteria"
            })
    except Exception as e:
        logging.error(e)
        error_response = {"message": f"An error occurred: {str(e)}"}
        response_data = responses.JSONResponse(error_response, status_code=500)

    return response_data


def release_iterator(db_conn: ReleaseAdaptor, site_name, release_label, current_only):

    # set release_label and site_name to None if it's an empty list
    release_label = release_label or None
    site_name = site_name or None

    release_results = db_conn.fetch_releases(
        site_name=site_name,
        release_label=release_label,
        current_only=current_only
    )

    for result in release_results:
        logger.debug(
            f"Processing release: {result.EnsemblRelease.version if hasattr(result, 'EnsemblRelease') else None}")
        yield create_release(result)


def test_get_releases(benchmark):

    response = client.get("/releases?release_name=2023-10-18")
    assert response.status_code == 200
    assert response.json() == [{"name": "2023-10-18",
                                "type":"partial",
                                "is_current":False}]

    response = client.get("/releases?current_only=true")
    assert response.status_code == 200
    assert response.json() == [{"name": "2025-02",
                                "type":"integrated",
                                "is_current":True},
                               {"name": "2026-01-26",
                                "type":"partial",
                                "is_current":True},
                              ]

    response = client.get("/releases?release_name=100000")
    assert response.status_code == 404

    response = client.get("/releases?release_name=2023-10-18&release_name=2024-09-18")
    assert response.status_code == 200
    assert response.json() == [{"name": "2023-10-18",
                                "type":"partial",
                                "is_current":False},
                               {"name": "2024-09-18",
                                "type":"partial",
                                "is_current":False}
                              ]

    response = client.get("/releases")
    assert response.status_code == 200
    assert len(response.json()) == 20

    runnable = lambda: client.get("/releases")
    benchmark(runnable)


# TODO: get data from DB
def data_get_genome_groups_with_reference(group_type, release_label):
    return (
        {
            "genomeGroups":
            [
                {
                    "groupId":"grch38-group",
                    "groupType":"structural_variant",
                    "groupName":None,
                    "referenceGenome":{
                        "organism": {
                            "scientificName":"Homo sapiens",
                            "speciesTaxonomyId":"9606",
                            "commonName":"Human",
                        },
                        "genomeUuid":"a7335667-93e7-11ec-a39d-005056b38ce3",
                        "type":None,
                        "assembly":{
                            "accession":"GCA_000001405.29",
                            "name":"GRCh38.p14",
                            "url":"https://identifiers.org/insdc.gca/GCA_000001405.29",
                            "isReference":True,
                            "urlName": "grch38"
                        },
                        "release":{
                            "releaseLabel":"2025-02",
                            "releaseType":"integrated",
                            "isCurrent":True
                        }
                    }
                }
            ]
        }
    )


@router.get("/genome_groups", name="genome_groups")
#@redis_cache("genome_groups", arg_keys=["group_type", "release"])
async def get_genome_groups(
        group_type: str = Query(..., description="Group type, e.g. 'structural_variant'"),
        release: str | None = Query(None, description="Optional release label, e.g. '2025-02'")
):
    try:
        genome_groups_dict = data_get_genome_groups_with_reference(
            group_type,
            release
        )
        logging.debug(f"genome_groups_dict: {genome_groups_dict}")
        if len(genome_groups_dict.get("genomeGroups", [])) == 0:
            return response_error_handler({
                "status": 404,
                "details": "No genome groups found matching criteria"
            })

        genome_groups = GenomeGroupsResponse(**genome_groups_dict)
        response_dict = genome_groups.model_dump()
        return responses.JSONResponse(response_dict, status_code=200)
    except Exception as ex:
        logging.exception("Error in get_genome_groups")
        return response_error_handler({"status": 500})


# TODO: get data from DB
def data_get_genomes_in_group(group_id, release_label):
    return (
        {
            "genomes":
            [
                {
                    "organism": {
                        "scientificName":"Homo sapiens",
                        "speciesTaxonomyId":"9606",
                        "commonName":"Human",
                    },
                    "genomeUuid":"a7335667-93e7-11ec-a39d-005056b38ce3",
                    "type":None,
                    "assembly":{
                        "accession":"GCA_000001405.29",
                        "name":"GRCh38.p14",
                        "url":"https://identifiers.org/insdc.gca/GCA_000001405.29",
                        "isReference":True,
                        "urlName": "grch38"
                    },
                    "release":{
                        "releaseLabel":"2025-02",
                        "releaseType":"integrated",
                        "isCurrent":True
                    }
                }
            ]
        }
    )

@router.get("/genome_groups/{group_id}/genomes", name="genomes_in_group")
#@redis_cache("genomes_in_group", arg_keys=["group_id", "release"])
async def get_genomes_in_group(
        group_id: str = Path(..., description="Group ID, e.g. 'grch38-group'"),
        release: str | None = Query(None, description="Optional release label, e.g. '2025-02'")
):
    try:
        genomes_in_group_dict = data_get_genomes_in_group(
                group_id,
                release
            )
        logging.debug(f"genomes_in_group_dict: {genomes_in_group_dict}")
        if len(genomes_in_group_dict.get("genomes", [])) == 0:
            return response_error_handler({
                "status": 404,
                "details": "No genomes found in specified group"
            })

        genomes_in_group = GenomesInGroupResponse(**genomes_in_group_dict)
        response_dict = genomes_in_group.model_dump()
        return responses.JSONResponse(response_dict, status_code=200)
    except Exception as ex:
        logging.exception("Error in get_genomes_in_group")
        return response_error_handler({"status": 500})



# TODO FIX: create stats data in DB and use
def data_get_genome_counts(db_conn: Any, release_label: str | None):

    try:
        # The logic calling the ORM and fetching data from the DB
        # will go here. For now, we return dummy data.
        dummy_data = {
            "total": 4758,
            "counts": [
                {
                    "label": "Animals",
                    "count": 4127,
                },
                {
                    "label": "Green Plants",
                    "count": 475,
                },
                {
                    "label": "Fungi",
                    "count": 116,
                },
                {
                    "label": "Bacteria",
                    "count": 1,
                },
                {
                    "label": "Others",
                    "count": 39,
                }
            ]
        }

        return dummy_data

    except Exception:
        # Dummy error handling until ORM logic is implemented.
        logger.exception(
            "Unexpected error while fetching genomes in group "
            "(release_label=%r)",release_label
        )
        return None



@router.get("/genome_counts", name="genome_counts")
#@redis_cache(key_prefix="genome_counts", arg_keys=["release"])
async def get_genome_counts(
	adaptor: GenomeAdaptorDep,
    release: str | None = Query(None, description="Optional release label to filter counts, e.g. '2025-02'")
):
    try:
        genome_counts_dict = data_get_genome_counts(adaptor, release)
        genome_counts = GenomeCountsResponse(**genome_counts_dict)
        response_data = responses.JSONResponse(genome_counts.model_dump(), status_code=200)
    except Exception as ex:
        logging.exception("Error in get_genome_counts")
        return response_error_handler({"status": 500})
    return response_data




app = FastAPI()
app.include_router(router)


client = TestClient(app)


def test_explain_genome():
    response = client.get("/genome/a7335667-93e7-11ec-a39d-005056b38ce3/explain")
    assert response.status_code == 200
    assert response.json() == {
        "genome_id":"a7335667-93e7-11ec-a39d-005056b38ce3",
        "genome_tag":None,
        "common_name":"Human",
        "scientific_name":"Homo sapiens",
        "species_taxonomy_id":"9606",
        "type":None,
        "is_reference":True,
        "assembly":{
            "accession_id":"GCA_000001405.29",
            "name":"GRCh38.p14"
        },
        "release":{
            "name":"2025-02",
            "type":"integrated"
        },
        "latest_genome":{
            "genome_id":"be73075e-0633-471d-b7c8-4f8ca7752a04",
            "genome_tag":None,
            "common_name":"Human",
            "scientific_name":"Homo sapiens",
            "species_taxonomy_id":"9606",
            "type":None,
            "is_reference":True,
            "assembly":{
                "accession_id":"GCA_000001405.29",
                "name":"GRCh38.p14",
                "url":"https://identifiers.org/insdc.gca/GCA_000001405.29"
            },
            "release":{
                "name":"2026-01-26",
                "type":"partial",
                "is_current":True
            }
        }
    }



def test_get_genomes_in_group():
    response = client.get("/genome_groups/grch38-group/genomes")
    assert response.status_code == 200
    assert response.json() == (
        {
            "genomes":
            [
                {"genome_id":"a7335667-93e7-11ec-a39d-005056b38ce3",
                 "genome_tag":"grch38",
                 "common_name":"Human",
                 "scientific_name":"Homo sapiens",
                 "species_taxonomy_id":"9606",
                 "type":None,
                 "is_reference":True,
                 "assembly":{
                     "accession_id":"GCA_000001405.29",
                     "name":"GRCh38.p14",
                     "url":"https://identifiers.org/insdc.gca/GCA_000001405.29"
                 },
                 "release":{
                     "name":"2025-02",
                     "type":"integrated",
                     "is_current":True
                 }
                }
            ]
        }
    )

def test_get_genome_groups():
    response = client.get("/genome_groups?group_type=structural_variant")
    assert response.status_code == 200
    assert response.json() == (
        {
            "genome_groups":
            [
                {
                    "id":"grch38-group",
                    "type":"structural_variant",
                    "name":None,
                    "reference_genome":{
                        "genome_id":"a7335667-93e7-11ec-a39d-005056b38ce3",
                        "genome_tag":"grch38",
                        "common_name":"Human",
                        "scientific_name":"Homo sapiens",
                        "species_taxonomy_id":"9606",
                        "type":None,
                        "is_reference":True,
                        "assembly":{
                            "accession_id":"GCA_000001405.29",
                            "name":"GRCh38.p14",
                            "url":"https://identifiers.org/insdc.gca/GCA_000001405.29"
                        },
                        "release":{
                            "name":"2025-02",
                            "type":"integrated",
                            "is_current":True
                        }
                    }
                }
            ]
        }
    )

def test_get_genome_counts():
    response = client.get("/genome_counts")
    assert response.status_code == 200
    assert response.json() == (
        {
            "total":4758,
            "counts":[
                {"label":"Animals","count":4127},
                {"label":"Green Plants","count":475},
                {"label":"Fungi","count":116},
                {"label":"Bacteria","count":1},
                {"label":"Others","count":39}
            ]
        }
    )

    # TODO: the response data is wrong here
    response = client.get("/genome_counts?release=2023-10-18")
    assert response.status_code == 200
    assert response.json() == (
        {
            "total":4758,
            "counts":[
                {"label":"Animals","count":4127},
                {"label":"Green Plants","count":475},
                {"label":"Fungi","count":116},
                {"label":"Bacteria","count":1},
                {"label":"Others","count":39}
            ]
        }
    )

