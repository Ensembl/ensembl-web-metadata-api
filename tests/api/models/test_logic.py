from types import SimpleNamespace

from api.models.logic import get_brief_genome_details_by_uuid

GENOME_UUID = "4273b9f0-c927-4215-87bf-828ef65de980"
LATEST_GENOME_UUID = "be73075e-0633-471d-b7c8-4f8ca7752a04"
ASSEMBLY_ACCESSION = "GCA_000001405.29"


class FakeGenomeAdaptor:
    def __init__(self, selected_genomes, assembly_genomes):
        self.selected_genomes = selected_genomes
        self.assembly_genomes = assembly_genomes
        self.genomes_by_uuid = {}
        self.genomes_by_url_name = {}
        for genome in selected_genomes:
            self.genomes_by_uuid.setdefault(genome.Genome.genome_uuid, []).append(
                genome
            )
        for genome in assembly_genomes:
            if genome.Genome.genome_uuid not in self.genomes_by_uuid:
                self.genomes_by_uuid[genome.Genome.genome_uuid] = [genome]
            if genome.Genome.url_name:
                self.genomes_by_url_name.setdefault(genome.Genome.url_name, []).append(
                    genome
                )

    def fetch_genomes(
        self, genome_uuid=None, release_version=None, assembly_accession=None
    ):
        if assembly_accession:
            return self.assembly_genomes
        if genome_uuid:
            return self.genomes_by_uuid.get(genome_uuid, self.selected_genomes)
        return []

    def fetch_genomes_by_url_name(self, url_name, release_version):
        return self.genomes_by_url_name.get(url_name, [])


def make_genome(
    release_type,
    is_current,
    accession=ASSEMBLY_ACCESSION,
    genome_release_is_current=None,
    genome_uuid=GENOME_UUID,
    url_name=ASSEMBLY_ACCESSION,
    release_label="2026-01",
    release_date=None,
):
    if genome_release_is_current is None:
        genome_release_is_current = is_current

    return SimpleNamespace(
        Genome=SimpleNamespace(
            genome_uuid=genome_uuid,
            created="2026-01-01",
            url_name=url_name,
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
            release_date=release_date,
            label=release_label,
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
    partial_genome = make_genome("partial", True, url_name=None)
    integrated_genome = make_genome("integrated", True)
    adaptor = FakeGenomeAdaptor([partial_genome], [partial_genome, integrated_genome])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_tag"] is None


def test_brief_genome_details_adds_latest_genome_for_old_uuid():
    old_genome = make_genome(
        "integrated",
        False,
        genome_uuid=GENOME_UUID,
        url_name=None,
        release_label="2025-02",
    )
    latest_genome = make_genome(
        "integrated",
        True,
        genome_uuid=LATEST_GENOME_UUID,
        release_label="2025-11",
    )
    adaptor = FakeGenomeAdaptor([old_genome], [old_genome, latest_genome])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_uuid"] == GENOME_UUID
    assert result["latest_genome"]["genome_uuid"] == LATEST_GENOME_UUID
    assert result["latest_genome"]["genome_tag"] == ASSEMBLY_ACCESSION


def test_brief_genome_details_adds_latest_integrated_for_archived_uuid():
    archived_genome = make_genome(
        "archive",
        False,
        genome_uuid=GENOME_UUID,
        url_name=None,
        release_label="2025-02",
    )
    latest_integrated = make_genome(
        "integrated",
        True,
        genome_uuid=LATEST_GENOME_UUID,
        release_label="2026-07",
    )
    adaptor = FakeGenomeAdaptor(
        [archived_genome], [archived_genome, latest_integrated]
    )

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_uuid"] == GENOME_UUID
    assert result["latest_genome"]["genome_uuid"] == LATEST_GENOME_UUID
    assert result["latest_genome"]["release"]["release_type"] == "integrated"


def test_brief_genome_details_adds_latest_partial_for_old_partial_uuid():
    old_partial = make_genome(
        "partial",
        False,
        genome_uuid=GENOME_UUID,
        url_name=None,
        release_label="2025-02-24",
    )
    latest_partial = make_genome(
        "partial",
        True,
        genome_uuid=LATEST_GENOME_UUID,
        url_name=None,
        release_label="2025-10-16",
    )
    adaptor = FakeGenomeAdaptor([old_partial], [old_partial, latest_partial])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["genome_uuid"] == GENOME_UUID
    assert result["latest_genome"]["genome_uuid"] == LATEST_GENOME_UUID


def test_brief_genome_details_omits_latest_for_partial_with_newer_integrated_only():
    partial_genome = make_genome(
        "partial",
        False,
        genome_uuid=GENOME_UUID,
        url_name=None,
        release_label="2025-02-24",
    )
    integrated_genome = make_genome(
        "integrated",
        True,
        genome_uuid=LATEST_GENOME_UUID,
        release_label="2025-11",
    )
    adaptor = FakeGenomeAdaptor([partial_genome], [partial_genome, integrated_genome])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["latest_genome"] is None


def test_brief_genome_details_omits_latest_for_integrated_with_newer_partial_only():
    integrated_genome = make_genome(
        "integrated",
        False,
        genome_uuid=GENOME_UUID,
        url_name=ASSEMBLY_ACCESSION,
        release_label="2025-02",
    )
    partial_genome = make_genome(
        "partial",
        True,
        genome_uuid=LATEST_GENOME_UUID,
        url_name=None,
        release_label="2025-02-24",
    )
    adaptor = FakeGenomeAdaptor([integrated_genome], [integrated_genome, partial_genome])

    result = get_brief_genome_details_by_uuid(adaptor, GENOME_UUID, None)

    assert result["latest_genome"] is None


def test_brief_genome_details_omits_latest_genome_for_accession():
    old_genome = make_genome(
        "integrated",
        False,
        genome_uuid=GENOME_UUID,
        url_name=None,
        release_label="2025-02",
    )
    latest_genome = make_genome(
        "integrated",
        True,
        genome_uuid=LATEST_GENOME_UUID,
        release_label="2025-11",
    )
    adaptor = FakeGenomeAdaptor([latest_genome], [old_genome, latest_genome])

    result = get_brief_genome_details_by_uuid(adaptor, ASSEMBLY_ACCESSION, None)

    assert result["genome_uuid"] == LATEST_GENOME_UUID
    assert result["latest_genome"] is None
