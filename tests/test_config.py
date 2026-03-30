import unittest

from starlette.datastructures import CommaSeparatedStrings

import api.config as config


class ConfigTestCase(unittest.TestCase):
    def test_environment_variables(self):
        assert type(config.ALLOWED_HOSTS) == CommaSeparatedStrings


if __name__ == "__main__":
    unittest.main()
