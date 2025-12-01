# MySQL Shell Python client

[![CI/CD Status][ci-status-badge]][ci-status-link]
[![Coverage Status][cov-status-badge]][cov-status-link]
[![Apache license][apache-license-badge]][apache-license-link]

MySQL Shell is an advanced client for MySQL Server that allow system administrator to perform both
cluster and instance level operations, using a single binary.

This project provides a Python client to perform the most common set of operations,
in addition to a set of predefined queries to cover most of the common use-cases.

## 🧑‍💻 Usage

1. Install the package from PyPi:
   ```shell
   pip install mysql-shell-client
   ```

2. Import and build the executors:
   ```python
   from mysql_shell.executors import LocalExecutor
   from mysql_shell.models import ConnectionDetails

   cluster_conn = ConnectionDetails(
       username="...",
       password="...",
       host="...",
       port="...",
   )
   instance_conn = ConnectionDetails(
       username="...",
       password="...",
       host="...",
       port="...",
   )
   
   cluster_executor = LocalExecutor(cluster_conn, "mysqlsh")
   instance_executor = LocalExecutor(instance_conn, "mysqlsh")
   ```

3. Import and build the query builders **[optional]**:
   ```python
   from mysql_shell.builders import CharmLockingQueryBuilder

   # This is just an example
   builder = CharmLockingQueryBuilder("mysql", "locking")
   query = builder.build_table_creation_query()
   rows = instance_executor.execute_sql(query)
   ```

4. Import and build the clients:
   ```python
   from mysql_shell.clients import MySQLClusterClient, MySQLInstanceClient
   
   cluster_client = MySQLClusterClient(cluster_executor)
   instance_client = MySQLClusterClient(instance_executor)
   ```


## 🔧 Development

### Dependencies
In order to install all the development packages:

```shell
poetry install --all-extras
```

### Linting
All Python files are linted using [Ruff][docs-ruff], to run it:

```shell
tox -e lint
```

### Testing
Project testing is performed using [Pytest][docs-pytest], to run them:

```shell
tox -e unit
```

```shell
export MYSQL_DATABASE="test"
export MYSQL_USERNAME="root"
export MYSQL_PASSWORD="root_pass"
export MYSQL_SHELL_PATH="..."

podman-compose -f compose/mysql-8.0.yaml up --detach && tox -e integration
podman-compose -f compose/mysql-8.0.yaml down
```

### Release
Commits can be tagged to create releases of the package, in order to do so:

1. Bump up the version within the `pyproject.toml` file.
2. Add a new section to the `CHANGELOG.md`.
3. Commit + push the changes.
4. Trigger the [release workflow][github-workflows].


[apache-license-badge]: https://img.shields.io/badge/License-Apache%202.0-blue.svg
[apache-license-link]: https://github.com/canonical/mysql-shell-client/blob/main/LICENSE
[ci-status-badge]: https://github.com/canonical/mysql-shell-client/actions/workflows/ci.yaml/badge.svg?branch=main
[ci-status-link]: https://github.com/canonical/mysql-shell-client/actions/workflows/ci.yaml?query=branch%3Amain
[cov-status-badge]: https://codecov.io/gh/canonical/mysql-shell-client/branch/main/graph/badge.svg
[cov-status-link]: https://codecov.io/gh/canonical/mysql-shell-client

[docs-pytest]: https://docs.pytest.org/en/latest/#
[docs-ruff]: https://docs.astral.sh/ruff/
[github-workflows]: https://github.com/canonical/mysql-shell-client/actions/workflows/release.yaml
