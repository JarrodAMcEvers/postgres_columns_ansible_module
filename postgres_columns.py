#!/usr/bin/python
from ansible.module_utils import basic
from ansible.module_utils.basic import *
import psycopg2 as psql
import psycopg2.extras

class PostgresColumnsHandler():
    query = "SELECT json_agg(column_name) as columns, table_name as table FROM information_schema.columns WHERE table_schema = 'public' AND table_name IN ("

    def getArgumentSpec(self):
        return {
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

    def setModuleParams(self, params):
        self.host = params['host']
        self.port = params['port']
        self.user = params['user']
        self.password = params['password']
        self.database = params['database']
        self.assertSchema = params['assert_schema']

    def connectToDatabase(self):
        self.connection = psql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)
        self.cursor = self.connection.cursor(cursor_factory=psql.extras.RealDictCursor)

    def getColumnsForTables(self):
        self.query += str().join(map(lambda x: "'{}',".format(x['table']), self.assertSchema))
        self.query = self.query[:-1]
        self.query += ') GROUP BY table_name'
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def assertColumnsExistForTables(self, results):
        if (len(results) == 0):
            return list(map(lambda x: { 'table': x['table'], 'missing_columns': x['columns']}, self.assertSchema))

        failedAssertions = []
        for row in results:
            tableColumns = row['columns']
            moduleColumns = list(map(lambda y: y['columns'], filter(lambda x: x['table'] == row['table'], self.assertSchema)))[0]
            difference = set(moduleColumns) - set(tableColumns)
            if len(difference) > 0:
                failedAssertions.append({ 'table': row['table'], 'missing_columns': list(difference) })
        return failedAssertions

def main():
    postgresColumns = PostgresColumnsHandler()
    module = basic.AnsibleModule(argument_spec=postgresColumns.getArgumentSpec())
    postgresColumns.setModuleParams(module.params)

    postgresColumns.connectToDatabase()
    queryResults = postgresColumns.getColumnsForTables()
    failedAssertions = postgresColumns.assertColumnsExistForTables(queryResults)
    if len(failedAssertions) > 0:
        return module.fail_json(msg='Failed validation: %s' % failedAssertions)
    else:
        return module.exit_json(changed=False, results={'results': 'passed'})

if __name__ == '__main__':
    main()
