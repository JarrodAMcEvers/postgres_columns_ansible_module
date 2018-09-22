#!/usr/bin/python
from ansible.module_utils import basic
from ansible.module_utils.basic import *
import psycopg2 as psql
import psycopg2.extras

class PostgresColumnsHandler():
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

    def connectToDatabase(self):
        psql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)

def main():
    postgresColumns = PostgresColumnsHandler()
    module = basic.AnsibleModule(argument_spec=postgresColumns.getArgumentSpec())
    postgresColumns.setModuleParams(module.params)

    postgresColumns.connectToDatabase()

if __name__ == '__main__':
    main()
