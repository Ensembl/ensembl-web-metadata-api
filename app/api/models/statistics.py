import logging
from pydantic import BaseModel
from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]


class Coding(BaseModel):
    coding_genes: int = None
    average_genomic_span: float = None
    average_sequence_length: float = None
    average_cds_length: float = None
    shortest_gene_length: float = None
    longest_gene_length: float = None
    total_transcripts: int = None
    coding_transcripts: float = None
    transcripts_per_gene: float = None
    coding_transcripts_per_gene: float = None
    total_exons: int = None
    total_coding_exons: int = None
    average_exon_length: float = None
    average_coding_exon_length: float = None
    average_exons_per_transcript: float = None
    average_coding_exons_per_coding_transcript: float = None
    total_introns: int = None
    average_intron_length: float = None


class GenomeStatistics(BaseModel):
    _raw_data: list
    _compiled_data: dict

    coding_stats: Coding

    def __init__(self, **data):
        data["_compiled_data"] = {
            stats_item["name"]: stats_item["statisticValue"]
            for stats_item in data["_raw_data"]
        }
        data["coding_stats"] = data["_compiled_data"]
        super().__init__(**data)
