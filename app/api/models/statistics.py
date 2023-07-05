import logging
from pydantic import BaseModel, Field
from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]


class Homology(BaseModel):
    homology: float = Field(alias="homology_coverage", default=None)
    coverage_explanation: str = None


class Regulation(BaseModel):
    enhancers: int = None
    promoters: int = None


class Pseudogene(BaseModel):
    pseudogenes: int = Field(alias="ps_pseudogenes", default=None)
    average_genomic_span: float = Field(alias="ps_average_genomic_span", default=None)
    average_sequence_length: float = Field(
        alias="ps_average_sequence_length", default=None
    )
    shortest_gene_length: int = Field(alias="ps_shortest_gene_length", default=None)
    longest_gene_length: int = Field(alias="ps_longest_gene_length", default=None)
    total_transcripts: int = Field(alias="ps_total_transcripts", default=None)
    transcripts_per_gene: float = Field(alias="ps_transcripts_per_gene", default=None)
    total_exons: int = Field(alias="ps_total_exons", default=None)
    average_exon_length: float = Field(alias="ps_average_exon_length", default=None)
    average_exons_per_transcript: float = Field(
        alias="ps_average_exons_per_transcript", default=None
    )
    total_introns: int = Field(alias="ps_total_introns", default=None)
    average_intron_length: float = Field(alias="ps_average_intron_length", default=None)


class NonCoding(BaseModel):
    non_coding_genes: int = Field(alias="nc_non_coding_genes", default=None)
    small_non_coding_genes: int = Field(alias="nc_small_non_coding_genes", default=None)
    long_non_coding_genes: int = Field(alias="nc_long_non_coding_genes", default=None)
    misc_non_coding_genes: int = Field(alias="nc_misc_non_coding_genes", default=None)
    average_genomic_span: float = Field(alias="nc_average_genomic_span", default=None)
    average_sequence_length: float = Field(
        alias="nc_average_sequence_length", default=None
    )
    shortest_gene_length: int = Field(alias="nc_shortest_gene_length", default=None)
    longest_gene_length: int = Field(alias="nc_longest_gene_length", default=None)
    total_transcripts: int = Field(alias="nc_total_transcripts")
    transcripts_per_gene: float = Field(alias="nc_transcripts_per_gene", default=None)
    total_exons: int = Field(alias="nc_total_exons", default=None)
    average_exon_length: float = Field(alias="nc_average_exon_length", default=None)
    average_exons_per_transcript: float = Field(
        alias="nc_average_exons_per_transcript", default=None
    )
    total_introns: int = Field(alias="nc_total_introns", default=None)
    average_intron_length: float = Field(alias="nc_average_intron_length", default=None)


class Coding(BaseModel):
    coding_genes: int = None
    average_genomic_span: float = None
    average_sequence_length: float = None
    average_cds_length: float = None
    shortest_gene_length: int = None
    longest_gene_length: int = None
    total_transcripts: int = None
    coding_transcripts: int = None
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


class Assembly(BaseModel):
    contig_n50: int = None
    total_genome_length: int = None
    total_coding_sequence_length: int = None
    total_gap_length: int = None
    spanned_gaps: int = None
    chromosomes: int = None
    toplevel_sequences: int = None
    component_sequences: int = None
    gc_percentage: float = None


class Variation(BaseModel):
    short_variants: int = None
    structural_variants: int = None
    short_variants_with_phenotype_assertions: int = None
    short_variants_with_publications: int = None
    short_variants_frequency_studies: int = None
    structural_variants_with_phenotype_assertions: int = None


class GenomeStatistics(BaseModel):
    _raw_data: list
    _compiled_data: dict

    assembly_stats: Assembly
    coding_stats: Coding
    variation_stats: Variation
    non_coding_stats: NonCoding
    pseudogene_stats: Pseudogene
    homology_stats: Homology
    regulation_stats: Regulation

    def __init__(self, **data):
        data["_compiled_data"] = {
            stats_item["name"]: stats_item["statisticValue"]
            for stats_item in data["_raw_data"]
            if stats_item["statisticValue"] != "null"
        }

        data["assembly_stats"] = data["_compiled_data"]
        data["coding_stats"] = data["_compiled_data"]
        data["variation_stats"] = data["_compiled_data"]
        data["non_coding_stats"] = data["_compiled_data"]
        data["pseudogene_stats"] = data["_compiled_data"]
        data["homology_stats"] = data["_compiled_data"]
        data["regulation_stats"] = data["_compiled_data"]

        super().__init__(**data)
