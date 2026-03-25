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

import logging
from typing import List

import sqlalchemy as db
from ensembl.utils.database import DBConnection
from ensembl.production.metadata.api.models.genome import Genome

from sqlalchemy import Column, Integer, create_engine, Index, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship, declarative_base
from sqlalchemy.orm.session import Session

from sqlalchemy.ext.declarative import DeferredReflection

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class GenomeTaxonomyCounts(DeferredReflection, Base):
    __tablename__ = "genome_taxonomy_counts"
    __table_args__ = {"extend_existing": True}
    genome_id = Column(Integer, primary_key=True)


class GenomeGroup(DeferredReflection, Base):
    __tablename__ = "genome_group"
    __table_args__ = {"extend_existing": True}
    genome_group_id = Column(Integer, primary_key=True)


class GenomeGroupMember(DeferredReflection, Base):
    __tablename__ = "genome_group_member"
    __table_args__ = {"extend_existing": True}
    genome_group_member_id = Column(Integer, primary_key=True)


class GenomeGroupCategory(DeferredReflection, Base):
    __tablename__ = "genome_group_category"
    __table_args__ = {"extend_existing": True}
    genome_group_category_id = Column(Integer, primary_key=True)


class MetaAdaptor:
    db_conn: DBConnection = None

    def __init__(self, db_conn: DBConnection):
        self.db_conn = db_conn
        DeferredReflection.prepare(db_conn._engine)

    def fetch_genome_taxonomy_counts(self, release_label: str | None = None):
        """
        Fetches genome taxonomy counts.

        Args:
            release_label: A release label, e.g. 2026-02

        Returns:
            List[Tuple[str, int]]: A list of tuples containing the fetched information.
            Each tuple contains the following elements:
                - ensembl_taxon_name: The taxon name we want to display on the
                    web site
                - count: Count of genomes in this taxon

        Example usage:
            genome_taxonomy_counts = fetch_genome_taxonomy_counts()
        """
        if release_label == None:
            release_label = ""
        with self.db_conn.session_scope() as session:
            sql = (
                db.select(
                    GenomeTaxonomyCounts.ensembl_taxon_name,
                    GenomeTaxonomyCounts.count,
                )
                .where(GenomeTaxonomyCounts.label == release_label)
                .order_by(GenomeTaxonomyCounts.ord)
            )
            logger.debug(sql)
            genome_taxonomy_counts = session.execute(sql).mappings().all()
        return genome_taxonomy_counts

    def fetch_genome_groups(self):
        """
        Fetches genome groups.

        Args:
            None

        Returns:
            List[GenomeGroup]: A list of GenomeGroup objects

        Example usage:
            genome_groups = fetch_genome_groups()
        """
        # select display_name, gg.type, gg.genome_group_id, name, label, description, count(genome_id) as genome_count
        # from genome_group gg
        # inner join genome_group_member gm on gm.genome_group_id = gg.genome_group_id
        # inner join genome_group_category gc on gc.type = gg.type
        # where gg.genome_group_id = 13 group by all;

        with self.db_conn.session_scope() as session:
            sql = (
                db.select(
                    GenomeGroup.type,
                    GenomeGroup.genome_group_id,
                    GenomeGroup.name,
                    GenomeGroup.label,
                    GenomeGroup.description,
                    GenomeGroupCategory.display_name,
                    func.count(GenomeGroupMember.genome_id).label("genome_count"),
                )
                .join(
                    GenomeGroupMember,
                    GenomeGroupMember.genome_group_id == GenomeGroup.genome_group_id,
                )
                .join(GenomeGroupCategory, GenomeGroupCategory.type == GenomeGroup.type)
                .group_by(
                    GenomeGroup.type,
                    GenomeGroup.genome_group_id,
                    GenomeGroup.name,
                    GenomeGroup.label,
                    GenomeGroup.description,
                    GenomeGroupCategory.display_name,
                )
                .order_by(GenomeGroup.genome_group_id)
            )
            logger.debug(sql)
            genome_groups = session.execute(sql).mappings().all()
        return genome_groups

    def fetch_genome_group_members(self, group_id: int):
        if group_id is None:
            raise ValueError

        with self.db_conn.session_scope() as session:
            sql = (
                db.select(Genome.genome_uuid)
                .join(
                    GenomeGroupMember, Genome.genome_id == GenomeGroupMember.genome_id
                )
                .where(GenomeGroupMember.genome_group_id == group_id)
                .order_by(Genome.genome_uuid)
            )
            logger.debug(sql)
            data = session.execute(sql).mappings().all()

        return data
