# See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from __future__ import annotations

import enum
import logging
import re
from operator import and_
from typing import List, Tuple, NamedTuple

import sqlalchemy as db
from ensembl.utils.database import DBConnection

from sqlalchemy import Column, Integer, create_engine, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, declarative_base
from sqlalchemy.orm.session import Session

from sqlalchemy.ext.declarative import DeferredReflection

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass

class GenomeTaxonomyCounts(DeferredReflection, Base):
    __tablename__ = 'genome_taxonomy_counts'
    __table_args__ = {'extend_existing': True}
    genome_id = Column(Integer, primary_key=True)

class MetaAdaptor():
    db_conn: DBConnection = None

    def __init__(self, db_conn: DBConnection):
        self.db_conn = db_conn
        DeferredReflection.prepare(db_conn._engine)

    def fetch_genome_taxonomy_counts(self):
        """
        Fetches genome taxonomy counts.

        Args:
            None

        Returns:
            List[Tuple[str, int]]: A list of tuples containing the fetched information.
            Each tuple contains the following elements:
                - ensembl_taxon_name: The taxon name we want to display on the
                    web site
                - count: Count of genomes in this taxon

        Example usage:
            genome_taxonomy_counts = fetch_genome_taxonomy_counts()
        """
        with self.db_conn.session_scope() as session:
            sql = db.select(
                GenomeTaxonomyCounts.ensembl_taxon_name,
                GenomeTaxonomyCounts.count,
            ).order_by(GenomeTaxonomyCounts.ord)
            logger.debug(sql)
            genome_taxonomy_counts = session.execute(sql).mappings().all()
        return genome_taxonomy_counts
