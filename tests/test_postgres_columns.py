import unittest
from postgres_columns import main, PostgresColumnsHandler
from ansible.module_utils import basic
from mock import MagicMock, patch
import psycopg2
from faker import Faker
fake = Faker('it_IT')

class TestPostgresColumnsHandler(unittest.TestCase):

    def setUp(self):
        self.postgresColumnsHandler = PostgresColumnsHandler()

        self.module = MagicMock()
        self.module.exit_json = MagicMock()
        basic.AnsibleModule = MagicMock(return_value=self.module)

    def testGetArgumentSpecReturnsTheExpectedDict(self):
        assert self.postgresColumnsHandler.getArgumentSpec() == {
            "host": { "required": True, "type": "str" },
            "port": { "required": True, "type": "int" },
            "user": { "required": True, "type": "str" },
            "password": { "required": True, "type": "str" },
            "database": { "required": True, "type": "str" },
            "assert_schema": { "required": True, "type": "list",
                "options": {
                    "table": { "required": True, "type": "str" },
                    "columns": { "required": True, "type": "list" }
                }
            }
        }

    def testAnsibleModuleIsCreated(self):
        main()

        basic.AnsibleModule.assert_called_with(argument_spec=self.postgresColumnsHandler.getArgumentSpec())