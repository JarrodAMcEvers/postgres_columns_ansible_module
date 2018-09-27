Ansible module that checks whether column(s) exist for a table(s) on a database.
The module fails if the column(s) do not exist on the table. Otherwise, life continues.

Usage in an ansible-playbook:
```
- name: make the query
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