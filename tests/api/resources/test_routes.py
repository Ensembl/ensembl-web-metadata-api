#
#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import unittest
from fastapi.testclient import TestClient

from api.main import app

import api.config as config

client = TestClient(app)


class APIMetadataTestCase(unittest.TestCase):

    def setUp(self):
        self.api_prefix = "api"
        self.metadata_url = "api/metadata/"
        self.statistics_url = self.metadata_url + "genome_counts"

    def test_404_error_in_none_relative_requests(self):
        response = client.get("api/")
        assert response.status_code == 404

    def test_api_error_404(self):
        get_response = client.get("/")
        assert get_response.status_code == 404

    def test_api_error_405(self):
        post_response = client.post(self.statistics_url)

        assert post_response.status_code == 405

        patch_response = client.patch(self.statistics_url)
        assert patch_response.status_code == 405

        delete_response = client.delete(self.statistics_url)
        assert delete_response.status_code == 405

        put_response = client.put(self.statistics_url)
        assert put_response.status_code == 405


def test_get_genome_counts():
    response = client.get("/api/metadata/genome_counts")
    assert response.status_code == 200
    assert response.json() == (
        {
            "total": 4758,
            "counts": [
                {"label": "Animals", "count": 4127},
                {"label": "Green Plants", "count": 475},
                {"label": "Fungi", "count": 116},
                {"label": "Bacteria", "count": 1},
                {"label": "Others", "count": 39},
            ],
        }
    )

    # TODO: the response data is wrong here
    response = client.get("/api/metadata/genome_counts?release=2023-10-18")
    assert response.status_code == 200
    assert response.json() == (
        {
            "total": 4758,
            "counts": [
                {"label": "Animals", "count": 4127},
                {"label": "Green Plants", "count": 475},
                {"label": "Fungi", "count": 116},
                {"label": "Bacteria", "count": 1},
                {"label": "Others", "count": 39},
            ],
        }
    )


def test_get_genomes_in_group():
    response = client.get("/api/metadata/genome_groups/grch38-group/genomes")
    assert response.status_code == 200
    assert response.json() == {
        "genomes": [
            {
                "genome_id": "a7335667-93e7-11ec-a39d-005056b38ce3",
                "genome_tag": "grch38",
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": None,
                "is_reference": True,
                "assembly": {
                    "accession_id": "GCA_000001405.29",
                    "name": "GRCh38.p14",
                    "url": "https://identifiers.org/insdc.gca/GCA_000001405.29",
                },
                "release": {
                    "name": "2025-02",
                    "type": "integrated",
                    "is_current": True,
                },
            },
            {
                "genome_id": "4c07817b-c7c5-463f-8624-982286bc4355",
                "genome_tag": "t2t-chm13",
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": None,
                "is_reference": False,
                "assembly": {
                    "accession_id": "GCA_009914755.4",
                    "name": "T2T-CHM13v2.0",
                    "url": "https://identifiers.org/insdc.gca/GCA_009914755.4",
                },
                "release": {
                    "name": "2025-02",
                    "type": "integrated",
                    "is_current": True,
                },
            },
            {
                "genome_id": "9d3b2ead-a987-4f08-8d18-10a1eb1e0fb0",
                "genome_tag": None,
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": {"kind": "population", "value": "Yoruban in Nigeria"},
                "is_reference": False,
                "assembly": {
                    "accession_id": "GCA_018503275.2",
                    "name": "NA19240_mat_hprc_f2",
                    "url": "https://identifiers.org/insdc.gca/GCA_018503275.2",
                },
                "release": {
                    "name": "2025-10-21",
                    "type": "partial",
                    "is_current": False,
                },
            },
            {
                "genome_id": "27be510b-c431-434c-a6f5-158d8c138507",
                "genome_tag": None,
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": {
                    "kind": "population",
                    "value": "Puerto Rican in Puerto Rico",
                },
                "is_reference": False,
                "assembly": {
                    "accession_id": "GCA_018506975.2",
                    "name": "HG00733_mat_hprc_f2",
                    "url": "https://identifiers.org/insdc.gca/GCA_018506975.2",
                },
                "release": {
                    "name": "2025-10-21",
                    "type": "partial",
                    "is_current": False,
                },
            },
            {
                "genome_id": "7e09bad9-aa22-46e4-ab8f-1b2a64202967",
                "genome_tag": None,
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": None,
                "is_reference": False,
                "assembly": {
                    "accession_id": "GCA_042077495.1",
                    "name": "NA19036_hap1_hprc_f2",
                    "url": "https://identifiers.org/insdc.gca/GCA_042077495.1",
                },
                "release": {
                    "name": "2025-05-28",
                    "type": "partial",
                    "is_current": False,
                },
            },
            {
                "genome_id": "30094672-c48c-425a-84e0-4049073a68d3",
                "genome_tag": None,
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": {"kind": "population", "value": "Colombian in Medellin"},
                "is_reference": False,
                "assembly": {
                    "accession_id": "GCA_018469665.2",
                    "name": "HG01123_mat_hprc_f2",
                    "url": "https://identifiers.org/insdc.gca/GCA_018469665.2",
                },
                "release": {
                    "name": "2025-10-21",
                    "type": "partial",
                    "is_current": False,
                },
            },
            {
                "genome_id": "82b440be-8f7d-47fe-a363-a40cea709ea2",
                "genome_tag": None,
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": {"kind": "population", "value": "Han Chinese South"},
                "is_reference": False,
                "assembly": {
                    "accession_id": "GCA_018472595.2",
                    "name": "HG00438_pat_hprc_f2",
                    "url": "https://identifiers.org/insdc.gca/GCA_018472595.2",
                },
                "release": {
                    "name": "2025-10-21",
                    "type": "partial",
                    "is_current": False,
                },
            },
            {
                "genome_id": "ddfadcb5-3b4a-48ca-9dcd-e75884445bd1",
                "genome_tag": None,
                "common_name": "Human",
                "scientific_name": "Homo sapiens",
                "species_taxonomy_id": "9606",
                "type": {"kind": "population", "value": "Peruvian in Lima"},
                "is_reference": False,
                "assembly": {
                    "accession_id": "GCA_018472695.2",
                    "name": "HG01928_mat_hprc_f2",
                    "url": "https://identifiers.org/insdc.gca/GCA_018472695.2",
                },
                "release": {
                    "name": "2025-10-21",
                    "type": "partial",
                    "is_current": False,
                },
            },
        ]
    }


def test_get_genome_groups():
    response = client.get("/api/metadata/genome_groups?group_type=structural_variant")
    assert response.status_code == 200
    assert response.json() == {
        "genome_groups": [
            {
                "id": "grch38-group",
                "type": "structural_variant",
                "name": None,
                "reference_genome": {
                    "genome_id": "a7335667-93e7-11ec-a39d-005056b38ce3",
                    "genome_tag": "grch38",
                    "common_name": "Human",
                    "scientific_name": "Homo sapiens",
                    "species_taxonomy_id": "9606",
                    "type": None,
                    "is_reference": True,
                    "assembly": {
                        "accession_id": "GCA_000001405.29",
                        "name": "GRCh38.p14",
                        "url": "https://identifiers.org/insdc.gca/GCA_000001405.29",
                    },
                    "release": {
                        "name": "2025-02",
                        "type": "integrated",
                        "is_current": True,
                    },
                },
            },
            {
                "id": "t2t-group",
                "type": "structural_variant",
                "name": None,
                "reference_genome": {
                    "genome_id": "4c07817b-c7c5-463f-8624-982286bc4355",
                    "genome_tag": "t2t-chm13",
                    "common_name": "Human",
                    "scientific_name": "Homo sapiens",
                    "species_taxonomy_id": "9606",
                    "type": None,
                    "is_reference": False,
                    "assembly": {
                        "accession_id": "GCA_009914755.4",
                        "name": "T2T-CHM13v2.0",
                        "url": "https://identifiers.org/insdc.gca/GCA_009914755.4",
                    },
                    "release": {
                        "name": "2025-02",
                        "type": "integrated",
                        "is_current": True,
                    },
                },
            },
        ]
    }


def test_get_releases(benchmark):

    response = client.get("/api/metadata/releases?release_name=2023-10-18")
    assert response.status_code == 200
    assert response.json() == [
        {"name": "2023-10-18", "type": "partial", "is_current": False}
    ]

    response = client.get("/api/metadata/releases?current_only=true")
    assert response.status_code == 200
    assert response.json() == [
        {"name": "2025-02", "type": "integrated", "is_current": True},
        {"name": "2026-01-26", "type": "partial", "is_current": True},
    ]

    response = client.get("/api/metadata/releases?release_name=100000")
    assert response.status_code == 404

    response = client.get(
        "/api/metadata/releases?release_name=2023-10-18&release_name=2024-09-18"
    )
    assert response.status_code == 200
    assert response.json() == [
        {"name": "2023-10-18", "type": "partial", "is_current": False},
        {"name": "2024-09-18", "type": "partial", "is_current": False},
    ]

    response = client.get("/api/metadata/releases")
    assert response.status_code == 200
    assert len(response.json()) == 20

    runnable = lambda: client.get("/api/metadata/releases")
    benchmark(runnable)


def test_get_vep_file_paths():
    response = client.get(
        "/api/metadata/genome/2b5fb047-5992-4dfb-b2fa-1fb4e18d1abb/vep/file_paths"
    )
    assert response.status_code == 200
    assert response.json() == {
        "faa_location": "Homo_sapiens/GCA_000001405.29/vep/genome/softmasked.fa.bgz",
        "gff_location": "Homo_sapiens/GCA_000001405.29/vep/ensembl/geneset/2024_11/genes.gff3.bgz",
    }


def test_get_genome_by_keyword():
    response = client.get(
        "/api/metadata/genomeid?assembly_accession_id=GCA_000001405.29"
    )
    assert response.status_code == 200
    assert response.json() == {
        "genome_uuid": "be73075e-0633-471d-b7c8-4f8ca7752a04",
        "release_version": 115.3,
        "genome_tag": "",
    }


def test_get_genome_dataset_attributes():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/dataset/genebuild/attributes"
    )
    assert response.status_code == 200
    assert response.json() == {
        "attributes": [
            {
                "name": "genebuild.stats.average_cds_length",
                "value": "1191.97",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.average_coding_exons_per_coding_transcript",
                "value": "7.98",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.average_coding_exons_per_transcript",
                "value": "8.13",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.average_coding_exon_length",
                "value": "149.38",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.average_exon_length",
                "value": "250.15",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.average_genomic_span",
                "value": "67396.48",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.average_intron_length",
                "value": "6172.48",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.average_sequence_legth",
                "value": "3566.92",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.coding_genes",
                "value": "20481",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.coding_transcripts",
                "value": "111076",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.coding_transcripts_per_gene",
                "value": "5.42",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.initial_release_date",
                "value": "2014-07",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.last_geneset_update",
                "value": "2023-03",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.level",
                "value": "toplevel",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.longest_gene_length",
                "value": "2473539",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.method",
                "value": "full_genebuild",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.method_display",
                "value": "Ensembl Genebuild",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_average_exons_per_transcript",
                "value": "3.50",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_average_exon_length",
                "value": "339.13",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_average_genomic_span",
                "value": "22981.34",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_average_sequence_length",
                "value": "967.28",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_longest_gene_length",
                "value": "1375317",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_long_non_coding_genes",
                "value": "18874",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_misc_non_coding_genes",
                "value": "2221",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_non_coding_genes",
                "value": "25959",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_shortest_gene_length",
                "value": "41",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_small_non_coding_genes",
                "value": "4864",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_total_introns",
                "value": "160555",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_total_transcripts",
                "value": "64262",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_transcripts_per_gene",
                "value": "2.48",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_average_exons_per_transcript",
                "value": "2.11",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_average_exon_length",
                "value": "371.37",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_average_genomic_span",
                "value": "3412.92",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_average_intron_length",
                "value": "4117.36",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_average_sequence_length",
                "value": "725.47",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_longest_gene_length",
                "value": "909387",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_pseudogenes",
                "value": "15239",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_shortest_gene_length",
                "value": "23",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_total_exons",
                "value": "35229",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_total_introns",
                "value": "18526",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_total_transcripts",
                "value": "16703",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.ps_transcripts_per_gene",
                "value": "1.10",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.shortest_gene_length",
                "value": "8",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.start_date",
                "value": "2014-01-Ensembl",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.total_coding_exons",
                "value": "886243",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.total_exons",
                "value": "1388435",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.total_introns",
                "value": "1217602",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.total_transcripts",
                "value": "170833",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.transcripts_per_gene",
                "value": "8.34",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.version",
                "value": "GENCODE44",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.sample_gene",
                "value": "ENSG00000221914",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.sample_location",
                "value": "8:26291508-26372680",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.id",
                "value": "39",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_average_intron_length",
                "value": "14932.57",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.havana_datafreeze_date",
                "value": "19-12-2022",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.provider_name",
                "value": "Ensembl",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.provider_url",
                "value": "https://www.ensembl.org",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.annotation_source",
                "value": "ensembl",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.stats.nc_total_exons",
                "value": "224817",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.provider_version",
                "value": "44",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "vep.faa_location",
                "value": "Homo_sapiens/GCA_000001405.29/vep/genome/softmasked.fa.bgz",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "vep.gff_location",
                "value": "Homo_sapiens/GCA_000001405.29/vep/ensembl/geneset/2023_03/genes.gff3.bgz",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_version",
                "value": "5.4.7",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_dataset",
                "value": "euarchontoglires_odb10",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco",
                "value": "C:99.7%[S:98.1%,D:1.6%],F:0.0%,M:0.3%,n:12692",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_mode",
                "value": "protein",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_completeness",
                "value": "12652",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_single_copy",
                "value": "12445",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_duplicated",
                "value": "207",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_fragmented",
                "value": "2",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_missing",
                "value": "38",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.busco_total",
                "value": "12692",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
            {
                "name": "genebuild.team_responsible",
                "value": "Genebuild",
                "version": "GENCODE44",
                "uuid": "949defef-c4d2-4ab1-8a73-f41d2b3c7719",
                "type": "genebuild",
            },
        ],
        "release_version": 1.0,
    }


def test_get_region_checksum():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/checksum/1"
    )
    assert response.status_code == 200
    assert response.content.decode("utf-8") == "2648ae1bacce4ec4b6cf337dcae37816"


def test_explain_genome():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/explain"
    )
    assert response.status_code == 200
    assert response.json() == {
        "genome_id": "a7335667-93e7-11ec-a39d-005056b38ce3",
        "genome_tag": None,
        "common_name": "Human",
        "scientific_name": "Homo sapiens",
        "species_taxonomy_id": "9606",
        "type": None,
        "is_reference": True,
        "assembly": {"accession_id": "GCA_000001405.29", "name": "GRCh38.p14"},
        "release": {"name": "2025-02", "type": "integrated"},
        "latest_genome": {
            "genome_id": "be73075e-0633-471d-b7c8-4f8ca7752a04",
            "genome_tag": None,
            "common_name": "Human",
            "scientific_name": "Homo sapiens",
            "species_taxonomy_id": "9606",
            "type": None,
            "is_reference": True,
            "assembly": {
                "accession_id": "GCA_000001405.29",
                "name": "GRCh38.p14",
                "url": "https://identifiers.org/insdc.gca/GCA_000001405.29",
            },
            "release": {"name": "2026-01-26", "type": "partial", "is_current": True},
        },
    }


def test_get_genome_ftplinks():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/ftplinks"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "dataset": "assembly",
            "url": "https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/genome",
        },
        {
            "dataset": "genebuild",
            "url": "https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/ensembl/geneset/2023_03",
        },
        {
            "dataset": "homologies",
            "url": "https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/ensembl/homology/2023_03",
        },
        {
            "dataset": "variation",
            "url": "https://ftp.ebi.ac.uk/pub/ensemblorganisms/Homo_sapiens/GCA_000001405.29/ensembl/variation/2023_03",
        },
    ]


def test_get_genome_details():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/details"
    )
    assert response.status_code == 200
    assert response.json() == {
        "genome_id": "a7335667-93e7-11ec-a39d-005056b38ce3",
        "genome_tag": None,
        "common_name": "Human",
        "scientific_name": "Homo sapiens",
        "species_taxonomy_id": "9606",
        "type": None,
        "is_reference": True,
        "assembly": {
            "accession_id": "GCA_000001405.29",
            "name": "GRCh38.p14",
            "url": "https://identifiers.org/insdc.gca/GCA_000001405.29",
        },
        "release": {"name": "2025-02", "type": "integrated"},
        "taxonomy_id": "9606",
        "assembly_provider": {
            "name": "Genome Reference Consortium",
            "url": "https://www.ncbi.nlm.nih.gov/grc",
        },
        "assembly_level": "chromosome",
        "assembly_date": "2013-12",
        "annotation_provider": {"name": "Ensembl", "url": "https://www.ensembl.org"},
        "annotation_method": "Ensembl Genebuild",
        "annotation_version": "44",
        "annotation_date": "2023-03",
        "number_of_genomes_in_group": 565,
    }


def test_example_objects():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/example_objects"
    )
    assert response.status_code == 200
    assert response.json() == [
        {"type": "gene", "id": "ENSG00000221914"},
        {"type": "location", "id": "8:26291508-26372680"},
        {"type": "variant", "id": "1:230710048:rs699"},
    ]


def test_validate_region():
    response = client.get(
        "/api/metadata/validate_location?genome_id=a7335667-93e7-11ec-a39d-005056b38ce3&location=8:26291508-26372680"
    )
    assert response.status_code == 200
    assert response.json() == {
        "region": {
            "error_code": None,
            "error_message": None,
            "region_name": "8",
            "is_valid": True,
        },
        "start": {
            "error_code": None,
            "error_message": None,
            "value": 26291508,
            "is_valid": True,
        },
        "end": {
            "error_code": None,
            "error_message": None,
            "value": 26372680,
            "is_valid": True,
        },
        "location": "8:26291508-26372680",
    }


def test_get_popular_species():
    response = client.get("/api/metadata/popular_species")
    assert response.status_code == 200
    assert response.json() == {
        "popular_species": [
            {
                "species_taxonomy_id": "9606",
                "name": "Human",
                "image": "//testserver/static/genome_images/9606.svg",
                "genomes_count": 565,
            },
            {
                "species_taxonomy_id": "10090",
                "name": "Mouse",
                "image": "//testserver/static/genome_images/10090.svg",
                "genomes_count": 31,
            },
            {
                "species_taxonomy_id": "7955",
                "name": "Zebrafish",
                "image": "//testserver/static/genome_images/7955.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "4565",
                "name": "Bread wheat",
                "image": "//testserver/static/genome_images/4565.svg",
                "genomes_count": 20,
            },
            {
                "species_taxonomy_id": "4530",
                "name": "Japanese rice",
                "image": "//testserver/static/genome_images/4530.svg",
                "genomes_count": 21,
            },
            {
                "species_taxonomy_id": "3702",
                "name": "Thale-cress",
                "image": "//testserver/static/genome_images/3702.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "9913",
                "name": "Cattle",
                "image": "//testserver/static/genome_images/9913.svg",
                "genomes_count": 5,
            },
            {
                "species_taxonomy_id": "10116",
                "name": "Norway rat",
                "image": "//testserver/static/genome_images/10116.svg",
                "genomes_count": 6,
            },
            {
                "species_taxonomy_id": "9823",
                "name": "Pig",
                "image": "//testserver/static/genome_images/9823.svg",
                "genomes_count": 29,
            },
            {
                "species_taxonomy_id": "4577",
                "name": "Maize",
                "image": "//testserver/static/genome_images/4577.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "9031",
                "name": "Chicken",
                "image": "//testserver/static/genome_images/9031.svg",
                "genomes_count": 5,
            },
            {
                "species_taxonomy_id": "9612",
                "name": "Dog",
                "image": "//testserver/static/genome_images/9612.svg",
                "genomes_count": 7,
            },
            {
                "species_taxonomy_id": "4513",
                "name": "Domesticated barley",
                "image": "//testserver/static/genome_images/4513.svg",
                "genomes_count": 69,
            },
            {
                "species_taxonomy_id": "7227",
                "name": "Fruit fly",
                "image": "//testserver/static/genome_images/7227.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "8090",
                "name": "Japanese medaka",
                "image": "//testserver/static/genome_images/8090.svg",
                "genomes_count": 15,
            },
            {
                "species_taxonomy_id": "9940",
                "name": "Sheep",
                "image": "//testserver/static/genome_images/9940.svg",
                "genomes_count": 22,
            },
            {
                "species_taxonomy_id": "29760",
                "name": "Wine grape",
                "image": "//testserver/static/genome_images/29760.svg",
                "genomes_count": 2,
            },
            {
                "species_taxonomy_id": "4081",
                "name": "Tomato",
                "image": "//testserver/static/genome_images/4081.svg",
                "genomes_count": 2,
            },
            {
                "species_taxonomy_id": "9796",
                "name": "Horse",
                "image": "//testserver/static/genome_images/9796.svg",
                "genomes_count": 3,
            },
            {
                "species_taxonomy_id": "3708",
                "name": "Oilseed rape",
                "image": "//testserver/static/genome_images/3708.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "4113",
                "name": "Potato",
                "image": "//testserver/static/genome_images/4113.svg",
                "genomes_count": 2,
            },
            {
                "species_taxonomy_id": "9986",
                "name": "Rabbit",
                "image": "//testserver/static/genome_images/9986.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "4932",
                "name": "Baker's yeast",
                "image": "//testserver/static/genome_images/4932.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "6239",
                "name": "Roundworm",
                "image": "//testserver/static/genome_images/6239.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "9685",
                "name": "Domestic cat",
                "image": "//testserver/static/genome_images/9685.svg",
                "genomes_count": 3,
            },
            {
                "species_taxonomy_id": "9544",
                "name": "Macaque",
                "image": "//testserver/static/genome_images/9544.svg",
                "genomes_count": 2,
            },
            {
                "species_taxonomy_id": "7994",
                "name": "Mexican tetra",
                "image": "//testserver/static/genome_images/7994.svg",
                "genomes_count": 6,
            },
            {
                "species_taxonomy_id": "4571",
                "name": "Durum wheat",
                "image": "//testserver/static/genome_images/4571.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "9598",
                "name": "Chimpanzee",
                "image": "//testserver/static/genome_images/9598.svg",
                "genomes_count": 3,
            },
            {
                "species_taxonomy_id": "8128",
                "name": "Nile tilapia",
                "image": "//testserver/static/genome_images/8128.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "9925",
                "name": "Goat",
                "image": "//testserver/static/genome_images/9925.svg",
                "genomes_count": 4,
            },
            {
                "species_taxonomy_id": "3712",
                "name": "Wild cabbage",
                "image": "//testserver/static/genome_images/3712.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "8364",
                "name": "Tropical clawed frog",
                "image": "//testserver/static/genome_images/8364.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "3847",
                "name": "Soybeans",
                "image": "//testserver/static/genome_images/3847.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "10029",
                "name": "Chinese hamster",
                "image": "//testserver/static/genome_images/10029.svg",
                "genomes_count": 3,
            },
            {
                "species_taxonomy_id": "3880",
                "name": "Barrel medic",
                "image": "//testserver/static/genome_images/3880.svg",
                "genomes_count": 2,
            },
            {
                "species_taxonomy_id": "3711",
                "name": "Field mustard",
                "image": "//testserver/static/genome_images/3711.svg",
                "genomes_count": 3,
            },
            {
                "species_taxonomy_id": "4558",
                "name": "Sorghum",
                "image": "//testserver/static/genome_images/4558.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "8030",
                "name": "Atlantic salmon",
                "image": "//testserver/static/genome_images/8030.svg",
                "genomes_count": 4,
            },
            {
                "species_taxonomy_id": "37682",
                "name": "Tausch's goatgrass",
                "image": "//testserver/static/genome_images/37682.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "562",
                "name": "Escherichia coli K-12",
                "image": "//testserver/static/genome_images/562.svg",
                "genomes_count": 1,
            },
            {
                "species_taxonomy_id": "5833",
                "name": "Malaria parasite",
                "image": "//testserver/static/genome_images/5833.svg",
                "genomes_count": 2,
            },
        ]
    }


def test_get_genome_karyotype():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/karyotype"
    )
    assert response.status_code == 200
    assert response.json() == [
        {"name": "1", "type": "chromosome", "length": 248956422, "is_circular": False},
        {"name": "2", "type": "chromosome", "length": 242193529, "is_circular": False},
        {"name": "3", "type": "chromosome", "length": 198295559, "is_circular": False},
        {"name": "4", "type": "chromosome", "length": 190214555, "is_circular": False},
        {"name": "5", "type": "chromosome", "length": 181538259, "is_circular": False},
        {"name": "6", "type": "chromosome", "length": 170805979, "is_circular": False},
        {"name": "7", "type": "chromosome", "length": 159345973, "is_circular": False},
        {"name": "8", "type": "chromosome", "length": 145138636, "is_circular": False},
        {"name": "9", "type": "chromosome", "length": 138394717, "is_circular": False},
        {"name": "10", "type": "chromosome", "length": 133797422, "is_circular": False},
        {"name": "11", "type": "chromosome", "length": 135086622, "is_circular": False},
        {"name": "12", "type": "chromosome", "length": 133275309, "is_circular": False},
        {"name": "13", "type": "chromosome", "length": 114364328, "is_circular": False},
        {"name": "14", "type": "chromosome", "length": 107043718, "is_circular": False},
        {"name": "15", "type": "chromosome", "length": 101991189, "is_circular": False},
        {"name": "16", "type": "chromosome", "length": 90338345, "is_circular": False},
        {"name": "17", "type": "chromosome", "length": 83257441, "is_circular": False},
        {"name": "18", "type": "chromosome", "length": 80373285, "is_circular": False},
        {"name": "19", "type": "chromosome", "length": 58617616, "is_circular": False},
        {"name": "20", "type": "chromosome", "length": 64444167, "is_circular": False},
        {"name": "21", "type": "chromosome", "length": 46709983, "is_circular": False},
        {"name": "22", "type": "chromosome", "length": 50818468, "is_circular": False},
        {"name": "X", "type": "chromosome", "length": 156040895, "is_circular": False},
        {"name": "Y", "type": "chromosome", "length": 57227415, "is_circular": False},
        {"name": "MT", "type": "chromosome", "length": 16569, "is_circular": False},
    ]


def test_get_metadata_statistics():
    response = client.get(
        "/api/metadata/genome/a7335667-93e7-11ec-a39d-005056b38ce3/stats"
    )
    assert response.status_code == 200
    assert response.json() == {
        "genome_stats": {
            "assembly_stats": {
                "contig_n50": 54806562,
                "total_genome_length": 3298912062,
                "total_coding_sequence_length": 34493611,
                "total_gap_length": 161611139,
                "spanned_gaps": 663,
                "chromosomes": 25,
                "toplevel_sequences": 709,
                "component_sequences": 36829,
                "gc_percentage": 38.88,
            },
            "coding_stats": {
                "coding_genes": 20481,
                "average_genomic_span": 67396.48,
                "average_sequence_length": None,
                "average_cds_length": 1191.97,
                "shortest_gene_length": 8,
                "longest_gene_length": 2473539,
                "total_transcripts": 170833,
                "coding_transcripts": 111076,
                "transcripts_per_gene": 8.34,
                "coding_transcripts_per_gene": 5.42,
                "total_exons": 1388435,
                "total_coding_exons": 886243,
                "average_exon_length": 250.15,
                "average_coding_exon_length": 149.38,
                "average_exons_per_transcript": None,
                "average_coding_exons_per_coding_transcript": None,
                "total_introns": 1217602,
                "average_intron_length": 6172.48,
            },
            "variation_stats": {
                "short_variants": 1099106974,
                "structural_variants": None,
                "short_variants_with_phenotype_assertions": None,
                "short_variants_with_publications": None,
                "short_variants_frequency_studies": None,
                "structural_variants_with_phenotype_assertions": None,
            },
            "non_coding_stats": {
                "non_coding_genes": 25959,
                "small_non_coding_genes": 4864,
                "long_non_coding_genes": 18874,
                "misc_non_coding_genes": 2221,
                "average_genomic_span": 22981.34,
                "average_sequence_length": 967.28,
                "shortest_gene_length": 41,
                "longest_gene_length": 1375317,
                "total_transcripts": 64262,
                "transcripts_per_gene": 2.48,
                "total_exons": 224817,
                "average_exon_length": 339.13,
                "average_exons_per_transcript": 3.5,
                "total_introns": 160555,
                "average_intron_length": 14932.57,
            },
            "pseudogene_stats": {
                "pseudogenes": 15239,
                "average_genomic_span": 3412.92,
                "average_sequence_length": 725.47,
                "shortest_gene_length": 23,
                "longest_gene_length": 909387,
                "total_transcripts": 16703,
                "transcripts_per_gene": 1.1,
                "total_exons": 35229,
                "average_exon_length": 371.37,
                "average_exons_per_transcript": 2.11,
                "total_introns": 18526,
                "average_intron_length": 4117.36,
            },
            "homology_stats": {
                "coverage": 91.6,
                "reference_species_name": "Pan troglodytes",
            },
            "regulation_stats": {
                "enhancers": 246403,
                "promoters": 35983,
                "ctcf_count": 90891,
                "tfbs_count": 30873,
                "open_chromatin_count": 7541,
            },
        }
    }


if __name__ == "__main__":
    unittest.main()
