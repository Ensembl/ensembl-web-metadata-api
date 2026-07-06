from types import SimpleNamespace

from api.models.logic import get_brief_genome_details_by_uuid

GENOME_UUID = "4273b9f0-c927-4215-87bf-828ef65de980"
LATEST_GENOME_UUID = "be73075e-0633-471d-b7c8-4f8ca7752a04"
ASSEMBLY_ACCESSION = "GCA_000001405.29"


class FakeGenomeAdaptor:
    def __init__(
        self, selected_genomes, assembly_genomes, best_genome_uuid=GENOME_UUID
    ):
        self.selected_genomes = selected_genomes
        self.assembly_genomes = assembly_genomes
        self.best_genome_uuid = best_genome_uuid
        self.genomes_by_uuid = {}
        for genome in selected_genomes:
            self.genomes_by_uuid.setdefault(genome.Genome.genome_uuid, []).append(
                genome
            )
        for genome in assembly_genomes:
            if genome.Genome.genome_uuid not in self.genomes_by_uuid:
                self.genomes_by_uuid[genome.Genome.genome_uuid] = [genome]

    def fetch_genomes(
        self, genome_uuid=None, release_version=None, assembly_accession=None
    ):
        if assembly_accession:
            return self.assembly_genomes
        if genome_uuid:
            return self.genomes_by_uuid.get(genome_uuid, self.selected_genomes)
        return []

    def get_genome_uuid_by_assembly_accession(self, assembly_accession, release):
        return self.best_genome_uuid


def make_genome(
    release_type,
    is_current,
    accession=ASSEMBLY_ACCESSION,
    genome_release_is_current=None,
    genome_uuid=GENOME_UUID,
):
    if genome_release_is_current is None:
        genome_release_is_current = is_current

    return SimpleNamespace(
        Genome=SimpleNamespace(
            genome_uuid=genome_uuid,
            created="2026-01-01",
            url_name="example_species",
            suppressed=False,
            suppression_details=None,
        ),
        Assembly=SimpleNamespace(
            assembly_uuid="assembly-uuid",
            accession=accession,
            level="chromosome",
            name="Example assembly",
            ucsc_name=None,
            ensembl_name=None,
            is_reference=False,
        ),
        Organism=SimpleNamespace(
            common_name="Example",
            strain=None,
            strain_type=None,
            scientific_name="Example species",
            biosample_id=None,
            scientific_parlance_name=None,
            organism_uuid="organism-uuid",
            taxonomy_id=1234,
            species_taxonomy_id=1234,
        ),
        EnsemblRelease=SimpleNamespace(
            version=1,
            release_date=None,
            label="2026-01",
            release_type=release_type,
            is_current=is_current,
        ),
        GenomeRelease=SimpleNamespace(
            is_current=genome_release_is_current,
        ),
        EnsemblSite=SimpleNamespace(
            name="ensembl",
            label="Ensembl",
            uri="https://www.ensembl.org",
        ),
    )


def test_brief_genome_details_assigns_tag_for_latest_integrated_genome():
    genome = make_genome("integrated", True)
    adaptor = FakeGenomeAdaptor([genome], [genome])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_tag"] == ASSEMBLY_ACCESSION
    assert result["latest_genome"] is None


def test_brief_genome_details_assigns_tag_for_latest_partial_without_integrated_genome():
    genome = make_genome("partial", False, genome_release_is_current=True)
    adaptor = FakeGenomeAdaptor([genome], [genome])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_tag"] == ASSEMBLY_ACCESSION
    assert result["latest_genome"] is None


def test_brief_genome_details_omits_tag_for_latest_partial_with_integrated_genome():
    partial_genome = make_genome("partial", True)
    integrated_genome = make_genome("integrated", True)
    adaptor = FakeGenomeAdaptor([partial_genome], [partial_genome, integrated_genome])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_tag"] is None


def test_brief_genome_details_adds_latest_genome_for_old_uuid():
    old_genome = make_genome("integrated", False, genome_uuid=GENOME_UUID)
    latest_genome = make_genome("integrated", True, genome_uuid=LATEST_GENOME_UUID)
    adaptor = FakeGenomeAdaptor(
        [old_genome],
        [old_genome, latest_genome],
        best_genome_uuid=LATEST_GENOME_UUID,
    )

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_uuid"] == GENOME_UUID
    assert result["latest_genome"]["genome_uuid"] == LATEST_GENOME_UUID
    assert result["latest_genome"]["genome_tag"] == ASSEMBLY_ACCESSION


def test_brief_genome_details_omits_latest_genome_for_accession():
    old_genome = make_genome("integrated", False, genome_uuid=GENOME_UUID)
    latest_genome = make_genome("integrated", True, genome_uuid=LATEST_GENOME_UUID)
    adaptor = FakeGenomeAdaptor(
        [latest_genome],
        [old_genome, latest_genome],
        best_genome_uuid=LATEST_GENOME_UUID,
    )

    result = get_brief_genome_details_by_uuid(adaptor, ASSEMBLY_ACCESSION, None)

    assert result["genome_uuid"] == LATEST_GENOME_UUID
    assert result["latest_genome"] is None
