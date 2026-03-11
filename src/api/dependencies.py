from ensembl.production.metadata.api.adaptors import (
    BaseAdaptor,
    GenomeAdaptor,
    ReleaseAdaptor,
)
from ensembl.production.metadata.api.adaptors.vep import VepAdaptor
from api.models.meta_adaptor import MetaAdaptor
from api.config import DB_URL
from ensembl.utils.database import DBConnection
import logging


class Dependencies:
    meta_conn = DBConnection(
        DB_URL, connect_args={"read_only": True, "config": {"memory_limit": "1GB"}}
    )

    genome_adaptor = GenomeAdaptor(meta_conn)
    vep_adaptor = VepAdaptor(meta_conn)
    release_adaptor = ReleaseAdaptor(meta_conn)
    meta_adaptor = MetaAdaptor(meta_conn)

    @staticmethod
    def get_genome_adaptor():
        return Dependencies.genome_adaptor

    @staticmethod
    def get_vep_adaptor():
        return Dependencies.vep_adaptor

    @staticmethod
    def get_release_adaptor():
        return Dependencies.release_adaptor

    @staticmethod
    def get_meta_adaptor():
        return Dependencies.meta_adaptor
