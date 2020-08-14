This ansible module asserts that a list of tables have the appropriate columns for a Postgres database.
The module will fail if the table does not exist or the table is missing any specified columns.


Usage in an ansible-playbook:
```
- name: check columns exist
  postgres_columns:
    host: 'localhost'
    port: 5432
    user: 'user'
    password: 'password'
    database: 'database'
    assert_schema:
    - table: 'table'
      columns:
      - 'column1'
      - 'other_column_i_care_about'
```
