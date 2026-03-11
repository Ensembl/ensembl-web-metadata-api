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


def test_get_genome_counts():
    meta_conn = DBConnection(
        DB_URL, connect_args={"read_only": True, "config": {"memory_limit": "1GB"}}
    )
    adaptor = MetaAdaptor(meta_conn)

    data = adaptor.fetch_genome_taxonomy_counts()
    assert data == [
        (0, "Genomes now available", 4852, 0),
        (33208, "Animals", 4195, 1),
        (2, "Bacteria", 1, 3),
        (4751, "Fungi", 151, 4),
        (33090, "Green Plants", 465, 5),
        (1, "Others", 40, 6),
    ]
