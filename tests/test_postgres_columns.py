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

        psycopg2.connect = MagicMock()

        self.module = MagicMock()
        self.module.params = {
            'database': fake.name(),
            'host': fake.name(),
            'port': fake.random_number(4),
            'user': fake.name(),
            'password': fake.name()
        }
        
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

    def testConnectToDatabaseWithModuleParams(self):
        main()

        psycopg2.connect.assert_called_with(
            host=self.module.params['host'],
            port=self.module.params['port'],
            user=self.module.params['user'],
            password=self.module.params['password'],
            database=self.module.params['database']
        )