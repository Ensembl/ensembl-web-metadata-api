#
#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import unittest
from api.models.meta_adaptor import MetaAdaptor
from api.config import DB_URL
from ensembl.utils.database import DBConnection
import logging


meta_conn = DBConnection(
    DB_URL, connect_args={"read_only": True, "config": {"memory_limit": "1GB"}}
)
adaptor = MetaAdaptor(meta_conn)


def test_get_genome_counts():
    data = adaptor.fetch_genome_taxonomy_counts()
    assert data == [
       {'ensembl_taxon_name': 'Animals', 'count': 4207},
       {'ensembl_taxon_name': 'Archaea', 'count': 24},
       {'ensembl_taxon_name': 'Bacteria', 'count': 85},
       {'ensembl_taxon_name': 'Fungi', 'count': 153},
       {'ensembl_taxon_name': 'Green Plants', 'count': 465},
       {'ensembl_taxon_name': 'Others', 'count': 43},
    ]

    data = adaptor.fetch_genome_taxonomy_counts("2026-01-26")
    assert data == [
        {"ensembl_taxon_name": "Animals", "count": 71},
        {"ensembl_taxon_name": "Fungi", "count": 4},
        {"ensembl_taxon_name": "Green Plants", "count": 1},
        {"ensembl_taxon_name": "Others", "count": 2},
    ]

# # This doesn't exist (yet)
# TODO: uncomment this once it's actually implemented
# def test_get_genome_groups():
#     data = adaptor.fetch_genome_groups()
#     assert data == []
