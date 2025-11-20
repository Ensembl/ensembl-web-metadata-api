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
from loguru import logger

import unittest
from fastapi.testclient import TestClient

from main import app


class APIMetadataTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.api_prefix = "api"
        self.metadata_url = "api/metadata/"
        self.statistics_url = self.metadata_url + "statistics"

    def test_statistics_api_success_200(self):
        get_response = self.client.get(self.statistics_url)
        assert get_response.status_code == 200
        assert type(get_response.json()) == dict

    def test_404_error_in_none_relative_requests(self):
        response = self.client.get("api/")
        assert response.status_code == 404

    def test_api_error_404(self):
        get_response = self.client.get("/")
        assert get_response.status_code == 404

    def test_api_error_405(self):
        post_response = self.client.post(self.statistics_url)

        assert post_response.status_code == 405

        patch_response = self.client.patch(self.statistics_url)
        assert patch_response.status_code == 405

        delete_response = self.client.delete(self.statistics_url)
        assert delete_response.status_code == 405

        put_response = self.client.put(self.statistics_url)
        assert put_response.status_code == 405


if __name__ == "__main__":
    unittest.main()
