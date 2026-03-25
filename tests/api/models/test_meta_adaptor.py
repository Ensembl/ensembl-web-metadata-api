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
from api.models.meta_adaptor import MetaAdaptor
from api.config import DB_URL
from ensembl.utils.database import DBConnection
import logging

meta_conn = DBConnection(
    DB_URL, connect_args={"read_only": True, "config": {"memory_limit": "1GB"}}
)
adaptor = MetaAdaptor(meta_conn)


def test_get_genome_counts():
    data = adaptor.fetch_genome_taxonomy_counts()
    assert data == [
        {"ensembl_taxon_name": "Animals", "count": 4207},
        {"ensembl_taxon_name": "Archaea", "count": 24},
        {"ensembl_taxon_name": "Bacteria", "count": 85},
        {"ensembl_taxon_name": "Fungi", "count": 153},
        {"ensembl_taxon_name": "Green Plants", "count": 465},
        {"ensembl_taxon_name": "Others", "count": 43},
    ]

    data = adaptor.fetch_genome_taxonomy_counts("2026-01-26")
    assert data == [
        {"ensembl_taxon_name": "Animals", "count": 71},
        {"ensembl_taxon_name": "Fungi", "count": 4},
        {"ensembl_taxon_name": "Green Plants", "count": 1},
        {"ensembl_taxon_name": "Others", "count": 2},
    ]


def test_get_genome_groups():
    data = adaptor.fetch_genome_groups()
    assert data == [
        {
            "type": "project",
            "genome_group_id": 12,
            "name": "vgp",
            "label": "Vertebrate Genomes Project (VGP)",
            "description": "The Vertebrate Genomes Project (VGP) is an international effort to generate near error-free, high-quality reference genome assemblies for all ~70,000 extant vertebrate species, advancing biology, conservation, and disease research.",
            "display_name": "External projects",
            "genome_count": 399,
        },
        {
            "type": "project",
            "genome_group_id": 13,
            "name": "erga-bge",
            "label": "Biodiversity Genomics Europe (BGE)",
            "description": "The ERGA-BGE project accelerates genomic science across Europe by generating high-quality reference genomes for biodiversity, supporting conservation, monitoring, and research as part of the Biodiversity Genomics Europe and Earth BioGenome initiatives.",
            "display_name": "External projects",
            "genome_count": 63,
        },
        {
            "type": "project",
            "genome_group_id": 14,
            "name": "aegis",
            "label": "Ancient Environmental Genomics Initiative for Sustainability (AEGIS)",
            "description": "AEGIS is a global research consortium using ancient environmental DNA and genomics to uncover past adaptations and genetic diversity, guiding development of climate-resilient crops and sustainable food systems under climate change.",
            "display_name": "External projects",
            "genome_count": 79,
        },
    ]


def test_get_genome_group_members():

    data = adaptor.fetch_genome_group_members(13)
    assert data == [
        {"genome_uuid": "085584f1-be77-4fd8-bb4b-55179438a77a"},
        {"genome_uuid": "0e692343-7207-4e4d-ae06-46327e0884b1"},
        {"genome_uuid": "0f03bee1-bdb9-4b0f-8fa4-4162d6fc4de0"},
        {"genome_uuid": "15dfef38-da6b-4090-9ba9-501272a54d72"},
        {"genome_uuid": "183fb547-fe4f-483f-93a6-33e806d8ffb4"},
        {"genome_uuid": "18cdfb34-0079-41ba-b551-0610d98a869e"},
        {"genome_uuid": "199ac9d9-9a12-42fe-ad46-ab919e1b7ea1"},
        {"genome_uuid": "1cd65d9f-f9c9-480b-8827-332c97d3a7e1"},
        {"genome_uuid": "20a32d3c-c6e5-4c72-9fed-223c3fcc7cce"},
        {"genome_uuid": "24c3b588-6437-4aef-b00d-97f1ff6db8c3"},
        {"genome_uuid": "2d09ff5e-5f83-4ead-af26-883f2aa90049"},
        {"genome_uuid": "2d6feac9-68ca-475a-b26a-e543f5617f7c"},
        {"genome_uuid": "2dce4529-d5c5-4380-90bb-fc9a93b14e26"},
        {"genome_uuid": "311af7cc-7b06-4af1-b7f0-a479530494e9"},
        {"genome_uuid": "3a017399-fbdd-4f75-a766-ddd353a23e61"},
        {"genome_uuid": "3dc4ba1b-5b1a-4788-8903-abb54df65971"},
        {"genome_uuid": "3e668946-a16d-49d7-af96-a6fa00aa9c95"},
        {"genome_uuid": "460b29ed-3ce3-4461-bd5e-4094a5e65d30"},
        {"genome_uuid": "4a1f953e-fcc1-4772-aae5-a7d85f896adf"},
        {"genome_uuid": "4cb15167-5eba-4a0e-89ff-ed7526a3b475"},
        {"genome_uuid": "4d0d28ca-9dd8-449b-8938-554fd1927dcb"},
        {"genome_uuid": "4fa77dd7-1ef3-43b6-b715-da7a5b1d2a4b"},
        {"genome_uuid": "5150ca1a-c085-49c1-8aeb-236bece9e2ac"},
        {"genome_uuid": "589ab9de-b4d3-4060-98a9-bd6f49b8165d"},
        {"genome_uuid": "61650ef3-65c0-4f37-9695-59bde3ddda4c"},
        {"genome_uuid": "624c4e99-7b00-4998-ab74-3299c4f791f4"},
        {"genome_uuid": "66abcf9f-42d0-4c7c-b6ae-fa8a39409d1b"},
        {"genome_uuid": "693b2899-2c0f-4a7b-8911-f52bb911c014"},
        {"genome_uuid": "773a6911-caee-4048-abe8-1be3bacf309e"},
        {"genome_uuid": "7b06a885-ead8-41aa-a36f-4af2ad43f6ff"},
        {"genome_uuid": "7f7df65a-cad2-4df3-a691-562103c3823c"},
        {"genome_uuid": "831f67ca-ad59-42db-97cf-2928163ba54c"},
        {"genome_uuid": "84d8aa9e-1f9e-40fe-a304-b3d2d5df1e9a"},
        {"genome_uuid": "8f02da11-38b0-4ce4-b9ff-44225adee5dc"},
        {"genome_uuid": "9059f588-83b9-4ab7-9dc5-1f121a6ac612"},
        {"genome_uuid": "92536bc5-9610-49d2-9d34-7bc93725e4c7"},
        {"genome_uuid": "9411dc39-a79c-444f-876f-8ded9239c07f"},
        {"genome_uuid": "a427b035-c8f5-4af1-b960-75177cbbbd8d"},
        {"genome_uuid": "a45e488b-c465-4bf4-9cf8-e40037ad3323"},
        {"genome_uuid": "ae315f68-16f6-493a-848b-16b381ea7c0e"},
        {"genome_uuid": "af787540-14c0-47e4-a5fa-d737ae99dd3f"},
        {"genome_uuid": "b06623a7-bd90-417a-9225-3a017a9e95f5"},
        {"genome_uuid": "b226bf95-1cf3-49ee-b653-1f5579aaa4e9"},
        {"genome_uuid": "b5224c43-5760-4ecc-8d70-8aa1cc1309ab"},
        {"genome_uuid": "b5c4a1a3-34b1-41ca-a06a-b0b1184f6eb2"},
        {"genome_uuid": "ba159eac-8428-4dd6-b0a7-35dad962cbea"},
        {"genome_uuid": "bd6e4578-1a73-4347-86e9-be824786e8ca"},
        {"genome_uuid": "c1090fd6-893b-4184-8896-13303cade69c"},
        {"genome_uuid": "daa9ab30-f5e7-45ad-9b7d-bb00e36d9014"},
        {"genome_uuid": "db285f3a-bbd6-454d-9908-b199da23d63b"},
        {"genome_uuid": "dd75a185-ff90-4c98-93c1-2a820123a452"},
        {"genome_uuid": "deaa01f4-be70-4e6e-b2a4-9d3c1aa54f92"},
        {"genome_uuid": "e63807d3-ebd9-443b-9615-51777ada1392"},
        {"genome_uuid": "e99525f8-b109-4002-974e-54dbab524cb3"},
        {"genome_uuid": "eabb8e38-7401-4fb6-8a26-2e3e4b92cb84"},
        {"genome_uuid": "eb483ac2-9422-4142-82d4-087b75623a5b"},
        {"genome_uuid": "ef8c4346-d4f4-4a5e-b91f-e27817698392"},
        {"genome_uuid": "ef91505c-33b6-4eb2-956c-513c0772e658"},
        {"genome_uuid": "efea712c-8fca-4d71-a7fb-f15b98402377"},
        {"genome_uuid": "f03a7d93-051e-4e02-8171-9363be133ffe"},
        {"genome_uuid": "f422268b-9c50-4ff8-8e69-922128901458"},
        {"genome_uuid": "f6e984dd-f7ba-457f-ba24-65e906f98d36"},
        {"genome_uuid": "fbb7fa5b-13fd-446f-875d-ddb2ab1f271d"},
    ]
