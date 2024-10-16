import logging

from pydantic import (
    BaseModel,
    Field,
    validator,
    field_serializer,
    root_validator,
    AliasChoices,
)
from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]

class Homology(BaseModel):
    coverage: float | None = Field(
        alias=AliasChoices("compara.stats.homology_coverage", "compara.homology_coverage", "compara.homology_coverage "),
        default=None,
    )
    reference_species_name: str | None = Field(
        alias=AliasChoices(
            "compara.stats.homology_reference_species", "compara.homology_reference_species", "compara.homology_reference_species "
        ),
        default=None,
    )

    @validator("reference_species_name", pre=True)
    def validate_na_values(cls, v) -> str:
        sanitized_reference_species_name = ""
        if v:
            sanitized_reference_species_name = v
        return sanitized_reference_species_name

    @field_serializer("reference_species_name")
    def serialize_refernce_species(self, value: str):
        if value == "":
            return None
        return value


class Regulation(BaseModel):
    enhancers: int | None = Field(
        alias=AliasChoices("regulation.stats.enhancer_count", "regulation.enhancer_count"),
        default=None
    )
    promoters: int | None = Field(
        alias=AliasChoices("regulation.stats.promoter_count", "regulation.promoter_count"),
        default=None
    )
    ctcf_count: int | None = Field(
        alias=AliasChoices("regulation.stats.ctcf_count", "regulation.ctcf_count"),
        default=None
    )
    tfbs_count: int | None = Field(
        alias=AliasChoices("regulation.stats.tfbs_count", "regulation.tfbs_count"),
        default=None
    )
    open_chromatin_count: int | None = Field(
        alias=AliasChoices("regulation.stats.open_chromatin_count", "regulation.open_chromatin_count"),
        default=None
    )


class Pseudogene(BaseModel):
    pseudogenes: int | None = Field(
        alias=AliasChoices("genebuild.stats.ps_pseudogenes", "genebuild.ps_pseudogenes"),
        default=None
    )
    average_genomic_span: float | None = Field(
        alias=AliasChoices("genebuild.stats.ps_average_genomic_span", "genebuild.ps_average_genomic_span"),
        default=None
    )
    average_sequence_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.ps_average_sequence_length", "genebuild.ps_average_sequence_length"),
        default=None
    )
    shortest_gene_length: int | None = Field(
        alias=AliasChoices("genebuild.stats.ps_shortest_gene_length", "genebuild.ps_shortest_gene_length"),
        default=None
    )
    longest_gene_length: int | None = Field(
        alias=AliasChoices("genebuild.stats.ps_longest_gene_length", "genebuild.ps_longest_gene_length"),
        default=None
    )
    total_transcripts: int | None = Field(
        alias=AliasChoices("genebuild.stats.ps_total_transcripts", "genebuild.ps_total_transcripts"),
        default=None
    )
    transcripts_per_gene: float | None = Field(
        alias=AliasChoices("genebuild.stats.ps_transcripts_per_gene", "genebuild.ps_transcripts_per_gene"),
        default=None
    )
    total_exons: int | None = Field(
        alias=AliasChoices("genebuild.stats.ps_total_exons", "genebuild.ps_total_exons"),
        default=None
    )
    average_exon_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.ps_average_exon_length", "genebuild.ps_average_exon_length"),
        default=None
    )
    average_exons_per_transcript: float | None = Field(
        alias=AliasChoices("genebuild.stats.ps_average_exons_per_transcript", "genebuild.ps_average_exons_per_transcript"),
        default=None
    )
    total_introns: int | None = Field(
        alias=AliasChoices("genebuild.stats.ps_total_introns", "genebuild.ps_total_introns"),
        default=None
    )
    average_intron_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.ps_average_intron_length", "genebuild.ps_average_intron_length"),
        default=None
    )


class NonCoding(BaseModel):
    non_coding_genes: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_non_coding_genes", "genebuild.nc_non_coding_genes"),
        default=None
    )
    small_non_coding_genes: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_small_non_coding_genes", "genebuild.nc_small_non_coding_genes"),
        default=None
    )
    long_non_coding_genes: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_long_non_coding_genes", "genebuild.nc_long_non_coding_genes"),
        default=None
    )
    misc_non_coding_genes: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_misc_non_coding_genes", "genebuild.nc_misc_non_coding_genes"),
        default=None
    )
    average_genomic_span: float | None = Field(
        alias=AliasChoices("genebuild.stats.nc_average_genomic_span", "genebuild.nc_average_genomic_span"),
        default=None
    )
    average_sequence_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.nc_average_sequence_length", "genebuild.nc_average_sequence_length"),
        default=None
    )
    shortest_gene_length: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_shortest_gene_length", "genebuild.nc_shortest_gene_length"),
        default=None
    )
    longest_gene_length: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_longest_gene_length", "genebuild.nc_longest_gene_length"),
        default=None
    )
    total_transcripts: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_total_transcripts", "genebuild.nc_total_transcripts"),
        default=None
    )
    transcripts_per_gene: float | None = Field(
        alias=AliasChoices("genebuild.stats.nc_transcripts_per_gene", "genebuild.nc_transcripts_per_gene"),
        default=None
    )
    total_exons: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_total_exons", "genebuild.nc_total_exons"),
        default=None
    )
    average_exon_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.nc_average_exon_length", "genebuild.nc_average_exon_length"),
        default=None
    )
    average_exons_per_transcript: float | None = Field(
        alias=AliasChoices("genebuild.stats.nc_average_exons_per_transcript", "genebuild.nc_average_exons_per_transcript"),
        default=None
    )
    total_introns: int | None = Field(
        alias=AliasChoices("genebuild.stats.nc_total_introns", "genebuild.nc_total_introns"),
        default=None
    )
    average_intron_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.nc_average_intron_length", "genebuild.nc_average_intron_length"),
        default=None
    )


class Coding(BaseModel):
    coding_genes: int | None = Field(
        alias=AliasChoices("genebuild.stats.coding_genes", "genebuild.coding_genes"),
        default=None
    )
    average_genomic_span: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_genomic_span", "genebuild.average_genomic_span"),
        default=None
    )
    average_sequence_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_sequence_length", "genebuild.average_sequence_length"),
        default=None
    )
    average_cds_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_cds_length", "genebuild.average_cds_length"),
        default=None
    )
    shortest_gene_length: int | None = Field(
        alias=AliasChoices("genebuild.stats.shortest_gene_length", "genebuild.shortest_gene_length"),
        default=None
    )
    longest_gene_length: int | None = Field(
        alias=AliasChoices("genebuild.stats.longest_gene_length", "genebuild.longest_gene_length"),
        default=None
    )
    total_transcripts: int | None = Field(
        alias=AliasChoices("genebuild.stats.total_transcripts", "genebuild.total_transcripts"),
        default=None
    )
    coding_transcripts: int | None = Field(
        alias=AliasChoices("genebuild.stats.coding_transcripts", "genebuild.coding_transcripts"),
        default=None
    )
    transcripts_per_gene: float | None = Field(
        alias=AliasChoices("genebuild.stats.transcripts_per_gene", "genebuild.transcripts_per_gene"),
        default=None
    )
    coding_transcripts_per_gene: float | None = Field(
        alias=AliasChoices("genebuild.stats.coding_transcripts_per_gene", "genebuild.coding_transcripts_per_gene"),
        default=None
    )
    total_exons: int | None = Field(
        alias=AliasChoices("genebuild.stats.total_exons", "genebuild.total_exons"),
        default=None
    )
    total_coding_exons: int | None = Field(
        alias=AliasChoices("genebuild.stats.total_coding_exons", "genebuild.total_coding_exons"),
        default=None
    )
    average_exon_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_exon_length", "genebuild.average_exon_length"),
        default=None
    )
    average_coding_exon_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_coding_exon_length", "genebuild.average_coding_exon_length"),
        default=None
    )
    average_exons_per_transcript: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_coding_exons_per_trans", "genebuild.average_coding_exons_per_trans"),
        default=None
    )
    average_coding_exons_per_coding_transcript: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_coding_exons_per_trans", "genebuild.average_coding_exons_per_trans"),
        default=None
    )
    total_introns: int | None = Field(
        alias=AliasChoices("genebuild.stats.total_introns", "genebuild.total_introns"),
        default=None
    )
    average_intron_length: float | None = Field(
        alias=AliasChoices("genebuild.stats.average_intron_length", "genebuild.average_intron_length"),
        default=None
    )


class Assembly(BaseModel):
    """
    I added AliasChoices temporarily for a smooth transition with breaking the API
    """
    contig_n50: int | None = Field(
        alias=AliasChoices("assembly.stats.contig_n50", "assembly.contig_n50"),
        default=None
    )
    total_genome_length: int | None = Field(
        alias=AliasChoices("assembly.stats.total_genome_length", "assembly.total_genome_length"),
        default=None
    )
    total_coding_sequence_length: int | None = Field(
        alias=AliasChoices("assembly.stats.total_coding_sequence_length", "assembly.total_coding_sequence_length"),
        default=None
    )
    total_gap_length: int | None = Field(
        alias=AliasChoices("assembly.stats.total_gap_length", "assembly.total_gap_length"),
        default=None
    )
    spanned_gaps: int | None = Field(
        alias=AliasChoices("assembly.stats.spanned_gaps", "assembly.spanned_gaps"),
        default=None
    )
    chromosomes: int | None = Field(
        alias=AliasChoices("assembly.stats.chromosomes", "assembly.chromosomes"),
        default=None
    )
    toplevel_sequences: int | None = Field(
        alias=AliasChoices("assembly.stats.toplevel_sequences", "assembly.toplevel_sequences"),
        default=None
    )
    component_sequences: int | None = Field(
        alias=AliasChoices("assembly.stats.component_sequences", "assembly.component_sequences"),
        default=None
    )
    gc_percentage: float | None = Field(
        alias=AliasChoices("assembly.stats.gc_percentage", "assembly.gc_percentage"),
        default=None
    )

    @validator("contig_n50", "component_sequences", pre=True)
    def validate_na_values(cls, v) -> int:
        if v == "NA":
            return -1
        return v

    @field_serializer("contig_n50", "component_sequences")
    def serialise_contig_n50(self, v: int):
        if v == -1:
            return None
        return v


class Variation(BaseModel):
    short_variants: int | None = Field(
        alias=AliasChoices("variation.stats.short_variants", "variation.short_variants"),
        default=None
    )
    structural_variants: int | None = Field(
        alias=AliasChoices("variation.stats.structural_variants", "variation.structural_variants"),
        default=None
    )
    short_variants_with_phenotype_assertions: int | None = Field(
        alias=AliasChoices("variation.stats.short_variants_with_phenotype_assertions", "variation.short_variants_with_phenotype_assertions"),
        default=None
    )
    short_variants_with_publications: int | None = Field(
        alias=AliasChoices("variation.stats.short_variants_with_publications", "variation.short_variants_with_publications"),
        default=None
    )
    short_variants_frequency_studies: int | None = Field(
        alias=AliasChoices("variation.stats.short_variants_frequency_studies", "variation.short_variants_frequency_studies"),
        default=None
    )
    structural_variants_with_phenotype_assertions: int | None = Field(
        alias=AliasChoices("variation.stats.structural_variants_with_phenotype_assertions", "variation.structural_variants_with_phenotype_assertions"),
        default=None
    )


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
                    data["_compiled_data"][stats_item["name"]] = stats_item.get("statisticValue", None)
                except KeyError as ke:
                    logging.error(ke)
                    logging.error(stats_item["name"], ke)
        except Exception as ex:
            logging.error("Error : ", ex)
        data["assembly_stats"] = data["_compiled_data"]
        data["coding_stats"] = data["_compiled_data"]
        data["variation_stats"] = data["_compiled_data"]
        data["non_coding_stats"] = data["_compiled_data"]
        data["pseudogene_stats"] = data["_compiled_data"]
        data["homology_stats"] = data["_compiled_data"]
        data["regulation_stats"] = data["_compiled_data"]

        super().__init__(**data)


class ExampleObject(BaseModel):
    type: str
    id: str


class ExampleObjectList(BaseModel):
    example_objects: list[ExampleObject] = []

    @root_validator(pre=True)
    def set_region_parameters(cls, values):
        extracted_example_objects = cls.extract_example_objects(
            values.get("example_objects")
        )
        values["example_objects"] = extracted_example_objects
        return values

    @staticmethod
    def extract_example_objects(genome_attributes):
        extracted_example_objects = []
        try:
            example_gene = ExampleObject(
                type="gene", id=genome_attributes["genebuildSampleGene"]
            )
            extracted_example_objects.append(example_gene)
            example_location = ExampleObject(
                type="location", id=genome_attributes["genebuildSampleLocation"]
            )
            extracted_example_objects.append(example_location)
            example_variant = ExampleObject(
                type="variant", id=genome_attributes["variationSampleVariant"]
            )
            extracted_example_objects.append(example_variant)
        except Exception as ex:
            logging.error(ex)
        return extracted_example_objects
