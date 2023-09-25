import logging
from pydantic import BaseModel, Field
from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]
from loguru import logger

class Homology(BaseModel):
    coverage: float = Field(alias="homology_coverage", default=None)
    coverage_explanation: str = None


class Regulation(BaseModel):
    enhancers: int = Field(alias="promoter.count", default=None)
    promoters: int = Field(alias="enhancer.count", default=None)


class Pseudogene(BaseModel):
    pseudogenes: int = Field(alias="genebuild.ps_pseudogenes", default=None)
    average_genomic_span: float = Field(alias="genebuild.ps_average_genomic_span", default=None)
    average_sequence_length: float = Field(
        alias="genebuild.ps_average_sequence_length", default=None
    )
    shortest_gene_length: int = Field(alias="genebuild.ps_shortest_gene_length", default=None)
    longest_gene_length: int = Field(alias="genebuild.ps_longest_gene_length", default=None)
    total_transcripts: int = Field(alias="genebuild.ps_total_transcripts", default=None)
    transcripts_per_gene: float = Field(alias="genebuild.ps_transcripts_per_gene", default=None)
    total_exons: int = Field(alias="genebuild.ps_total_exons", default=None)
    average_exon_length: float = Field(alias="genebuild.ps_average_exon_length", default=None)
    average_exons_per_transcript: float = Field(
        alias="genebuild.ps_average_exons_per_transcript", default=None
    )
    total_introns: int = Field(alias="genebuild.ps_total_introns", default=None)
    average_intron_length: float = Field(alias="genebuild.ps_average_intron_length", default=None)


class NonCoding(BaseModel):
    non_coding_genes: int = Field(alias="genebuild.nc_non_coding_genes", default=None)
    small_non_coding_genes: int = Field(alias="genebuild.nc_small_non_coding_genes", default=None)
    long_non_coding_genes: int = Field(alias="genebuild.nc_long_non_coding_genes", default=None)
    misc_non_coding_genes: int = Field(alias="genebuild.nc_misc_non_coding_genes", default=None)
    average_genomic_span: float = Field(alias="genebuild.nc_average_genomic_span", default=None)
    average_sequence_length: float = Field(
        alias="genebuild.nc_average_sequence_length", default=None
    )
    shortest_gene_length: int = Field(alias="genebuild.nc_shortest_gene_length", default=None)
    longest_gene_length: int = Field(alias="genebuild.nc_longest_gene_length", default=None)
    total_transcripts: int = Field(alias="genebuild.nc_total_transcripts")
    transcripts_per_gene: float = Field(alias="genebuild.nc_transcripts_per_gene", default=None)
    total_exons: int = Field(alias="genebuild.nc_total_exons", default=None)
    average_exon_length: float = Field(alias="genebuild.nc_average_exon_length", default=None)
    average_exons_per_transcript: float = Field(
        alias="genebuild.nc_average_exons_per_transcript", default=None
    )
    total_introns: int = Field(alias="genebuild.nc_total_introns", default=None)
    average_intron_length: float = Field(alias="genebuild.nc_average_intron_length", default=None)


class Coding(BaseModel):
    coding_genes: int = Field(alias="genebuild.coding_genes", default=None)
    average_genomic_span: float = Field(alias="genebuild.average_genomic_span", default=None)
    average_sequence_length: float = Field(alias="genebuild.average_sequence_length", default=None)
    average_cds_length: float = Field(alias="genebuild.average_cds_length", default=None)
    shortest_gene_length: int = Field(alias="genebuild.shortest_gene_length", default=None)
    longest_gene_length: int = Field(alias="genebuild.longest_gene_length", default=None)
    total_transcripts: int = Field(alias="genebuild.total_transcripts", default=None)
    coding_transcripts: int = Field(alias="genebuild.coding_transcripts", default=None)
    transcripts_per_gene: float = Field(alias="genebuild.transcripts_per_gene", default=None)
    coding_transcripts_per_gene: float = Field(alias="genebuild.coding_transcripts_per_gene", default=None)
    total_exons: int = Field(alias="genebuild.total_exons", default=None)
    total_coding_exons: int = Field(alias="genebuild.total_coding_exons", default=None)
    average_exon_length: float = Field(alias="genebuild.average_exon_length", default=None)
    average_coding_exon_length: float = Field(alias="genebuild.average_coding_exon_length", default=None)
    average_exons_per_transcript: float = Field(alias="genebuild.average_coding_exons_per_trans", default=None)
    average_coding_exons_per_coding_transcript: float = Field(alias="genebuild.average_coding_exons_per_trans", default=None)
    total_introns: int = Field(alias="genebuild.total_introns", default=None)
    average_intron_length: float = Field(alias="genebuild.", default=None)


class Assembly(BaseModel):
    contig_n50: int = Field(alias="assembly.contig_n50", default=None)
    total_genome_length: int = Field(alias="assembly.total_genome_length", default=None)
    total_coding_sequence_length: int = Field(alias="assembly.total_coding_sequence_length", default=None)
    total_gap_length: int = Field(alias="assembly.total_gap_length", default=None)
    spanned_gaps: int = Field(alias="assembly.spanned_gaps", default=None)
    chromosomes: int = Field(alias="assembly.chromosomes", default=None)
    toplevel_sequences: int = Field(alias="assembly.toplevel_sequences", default=None)
    component_sequences: int = Field(alias="assembly.component_sequences", default=None)
    gc_percentage: float = Field(alias="assembly.gc_percentage", default=None)


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
        data["_compiled_data"] = {}
        try:
            for stats_item in data["_raw_data"]:
                try:
                    data["_compiled_data"][stats_item["name"]]=stats_item["statisticValue"]
                except KeyError as ke:
                    logger.debug(ke)
        except Exception as ex:
            logger.debug(ex)
        data["assembly_stats"] = data["_compiled_data"]
        data["coding_stats"] = data["_compiled_data"]
        data["variation_stats"] = data["_compiled_data"]
        data["non_coding_stats"] = data["_compiled_data"]
        data["pseudogene_stats"] = data["_compiled_data"]
        data["homology_stats"] = data["_compiled_data"]
        data["regulation_stats"] = data["_compiled_data"]

        super().__init__(**data)
