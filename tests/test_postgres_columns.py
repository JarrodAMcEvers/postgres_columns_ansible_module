import unittest
from postgres_columns import main, PostgresColumnsHandler
from ansible.module_utils import basic
from mock import MagicMock, patch, call
import psycopg2
from faker import Faker
fake = Faker('it_IT')

class TestPostgresColumnsHandler(unittest.TestCase):

    def setUp(self):
        self.postgresColumnsHandler = PostgresColumnsHandler()

        self.cursor = MagicMock()
        self.cursor.execute = MagicMock()

        self.connection = MagicMock()
        self.connection.cursor = MagicMock(return_value=self.cursor)
        psycopg2.connect = MagicMock(return_value=self.connection)
        psycopg2.extras = MagicMock()
        psycopg2.extras.RealDictCursor = MagicMock()

        self.module = MagicMock()
        self.module.params = {
            'database': fake.name(),
            'host': fake.name(),
            'port': fake.random_number(4),
            'user': fake.name(),
            'password': fake.name(),
            'assert_schema': [{ 'table': 'table', 'columns': [] }]
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
                    "columns": { "required": True, "type": "list",
                        "options": {
                            "name": { "required": True, "type": "str" },
                            "type": { "required": True, "type": "str" }
                        }
                    }
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

    def testQueryTheDatabaseForAllTheTablesGiven(self):
        table = fake.name()
        table2 = fake.name()
        self.module.params['assert_schema'] = []
        self.module.params['assert_schema'].append({ 'table': table, 'columns': [] })
        self.module.params['assert_schema'].append({ 'table': table2, 'columns': [] })

        main()

        self.connection.cursor.assert_called_with(cursor_factory=psycopg2.extras.RealDictCursor)
        assert self.cursor.execute.call_args_list[0] == call("SELECT json_agg(column_name) as columns, table_name as table FROM information_schema.columns WHERE table_schema = 'public' AND table_name IN ('" + table + "','" + table2 + "') GROUP BY table_name")

    def testReturnsFailJsonIfTableDoesNotHaveTheColumnsGiven(self):
        table = fake.name()
        self.module.params['assert_schema'] = []
        self.module.params['assert_schema'].append({ 'table': table, 'columns': ['col1'] })

        self.cursor.fetchall = MagicMock(return_value=[{ 'table': table, 'columns': [] }])

        expectedMessage = [{ 'table': table, 'missing_columns': ['col1'] }]
        main()

        self.module.fail_json.assert_called_with(msg="Failed validation: %s" % expectedMessage)

    def testReturnsFailJsonIfTheTableDoesNotExist(self):
        column = fake.street_suffix()
        table = fake.name()
        self.module.params['assert_schema'] = []
        self.module.params['assert_schema'].append({ 'table': table, 'columns': [column] })

        expectedMessage = [{ 'table': table, 'missing_columns': [column] }]
        self.cursor.fetchall = MagicMock(return_value=[])

        main()

        self.module.fail_json.assert_called_with(msg='Failed validation: %s' % expectedMessage)

    def testReturnsExitJsonIfValidationPasses(self):
        table = fake.name()
        self.module.params['assert_schema'] = []
        self.module.params['assert_schema'].append({ 'table': table, 'columns': ['col1'] })

        self.cursor.fetchall = MagicMock(return_value=[{ 'table': table, 'columns': ['col1', 'col2', 'other_col'] }])

        expectedMessage = { 'passed': True }
        main()

        self.module.exit_json.assert_called_with(changed=False, results=expectedMessage)

    def testReturnsExitJsonIfTheDatabaseHasMoreColumnsThanWhatGiven(self):
        table = fake.name()
        self.module.params['assert_schema'] = []
        self.module.params['assert_schema'].append({ 'table': table, 'columns': ['col1'] })

        self.cursor.fetchall = MagicMock(return_value=[{ 'table': table, 'columns': ['col1', 'col2', 'col3', 'col4'] }])

        expectedMessage = { 'passed': True }
        main()

        self.module.exit_json.assert_called_with(changed=False, results=expectedMessage)
