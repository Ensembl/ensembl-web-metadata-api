from api.schemas.genome import GenomeDetails


def minimal_genome_details_data():
    return {
        "genome_uuid": "4273b9f0-c927-4215-87bf-828ef65de98",
        "organism": {
            "scientific_name": "Example species",
            "species_taxonomy_id": 1234,
            "taxonomy_id": 1234,
        },
        "assembly": {
            "accession": "GCA_000001405.29",
            "name": "Example assembly",
            "is_reference": False,
        },
        "release": {
            "release_label": "2026-05",
            "release_type": "integrated",
        },
        "attributes_info": {
            "assembly_level": "chromosome",
            "assembly_provider_name": "Assembly Provider",
            "assembly_provider_url": None,
            "genebuild_provider_name": "Annotation Provider",
            "genebuild_provider_url": None,
        },
    }


def test_genome_details_accepts_null_provider_urls():
    genome_details = GenomeDetails(**minimal_genome_details_data())

    data = genome_details.model_dump()

    assert data["assembly_provider"] == {
        "name": "Assembly Provider",
        "url": None,
    }
    assert data["annotation_provider"] == {
        "name": "Annotation Provider",
        "url": None,
    }
