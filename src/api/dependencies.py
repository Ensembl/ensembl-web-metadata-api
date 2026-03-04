from ensembl.production.metadata.api.adaptors import BaseAdaptor, GenomeAdaptor, ReleaseAdaptor
from ensembl.production.metadata.api.adaptors.vep import VepAdaptor
from api.config import DB_URL
from ensembl.utils.database import DBConnection
import logging

#def patch__init__(self, db_conn):
#    self.metadata_db = db_conn
#
#BaseAdaptor.__init = patch__init__


class Dependencies:
    meta_conn = DBConnection(
        DB_URL, connect_args={
            'read_only': True,
            'config': {
                'memory_limit': '1GB'
            }
        }
    )

#    class MyGenomeAdaptor(GenomeAdaptor):
#        def __init__(self, db_conn):
#            self.metadata_db = db_conn
#            self.taxonomy_db = db_conn
#
#    class MyVepAdaptor(VepAdaptor):
#        def __init__(self, db_conn, file="all"):
#            self.metadata_db = db_conn
#            self.file = file
#
#    class MyReleaseAdaptor(ReleaseAdaptor):
#        def __init__(self, db_conn):
#            self.metadata_db = db_conn

    genome_adaptor = GenomeAdaptor(meta_conn)
    vep_adaptor = VepAdaptor(meta_conn)
    release_adaptor = ReleaseAdaptor(meta_conn)

    @staticmethod
    def get_genome_adaptor():
        logging.warn("zip")
        return Dependencies.genome_adaptor

    def get_vep_adaptor():
        logging.warn("zap")
        return Dependencies.vep_adaptor

    def get_release_adaptor():
        logging.warn("zup")
        return Dependencies.release_adaptor


