import logging
from pydantic import BaseModel
from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]


class Contig(BaseModel):
    coding_genes: int = None
    average_genomic_span: int = None
    average_sequence_length: int = None
    average_cds_length: int = None
    shortest_gene_length: int = None
    longest_gene_length: int = None
    total_transcripts: int = None
    coding_transcripts: int = None
    transcripts_per_gene: int = None
    coding_transcripts_per_gene: int = None
    total_exons: int = None
    total_coding_exons: int = None
    average_exon_length: int = None
    average_coding_exon_length: int = None
    average_exons_per_transcript: int = None
    average_coding_exons_per_coding_transcript: int = None
    total_introns: int = None
    average_intron_length: int = None


class GenomeStatS(BaseModel):
    contig_stats: Contig
