Ansible module that checks whether column(s) exist for a table(s) on a database.
The module fails if the column(s) do not exist on the table or if the table specificed does not exist.

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
