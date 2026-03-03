from ensembl.production.metadata.api.adaptors import GenomeAdaptor, ReleaseAdaptor
from ensembl.production.metadata.api.adaptors.vep import VepAdaptor
from ensembl.utils.database import DBConnection

meta_conn = DBConnection(DB_URL)
genome_adaptor = GenomeAdaptor(meta_conn)
vep_adaptor = VepAdaptor(meta_conn)
release_adaptor = ReleaseAdaptor(meta_conn)


def get_genome_adaptor():
    yield genome_adaptor


def get_vep_adaptor():
    yield vep_adaptor


def get_release_adaptor():
    yield release_adaptor


