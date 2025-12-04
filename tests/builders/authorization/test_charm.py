# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from mysql_shell.builders import CharmAuthorizationQueryBuilder
from mysql_shell.executors import LocalExecutor
from mysql_shell.executors.errors import ExecutionError
from mysql_shell.models.account import Role
from mysql_shell.models.statement import VariableScope

from ...helpers import (
    build_local_executor,
    temp_variable,
)


@pytest.mark.integration
class TestCharmAuthorizationQueryBuilder:
    """Class to group all the CharmAuthorizationQueryBuilder tests."""

    DB_CREATE_QUERY = "CREATE DATABASE IF NOT EXISTS test"
    TABLE_CREATE_QUERY = "CREATE TABLE IF NOT EXISTS test.roles (id SERIAL PRIMARY KEY, name TEXT)"
    TABLE_INSERT_QUERY = "INSERT INTO test.roles (name) VALUES ('new-role')"
    TABLE_SELECT_QUERY = "SELECT name FROM test.roles"

    @pytest.fixture(scope="class", autouse=True)
    def executor(self):
        """Local executor fixture."""
        return build_local_executor(
            username=os.environ["MYSQL_USERNAME"],
            password=os.environ["MYSQL_PASSWORD"],
        )

    @pytest.fixture(scope="class", autouse=True)
    def config(self):
        """Database config fixture."""
        with temp_variable(VariableScope.GLOBAL, "activate_all_roles_on_login", "ON"):
            yield

    @staticmethod
    def _delete_role(executor: LocalExecutor, role: Role):
        """Get the granted roles for a user."""
        query = "DROP ROLE IF EXISTS '{rolename}'@'{hostname}'"
        query = query.format(
            rolename=role.rolename,
            hostname=role.hostname,
        )

        executor.execute_sql(query)

    def test_instance_auth_roles_query(self, executor: LocalExecutor):
        """Test the creation of instance auth roles."""
        builder = CharmAuthorizationQueryBuilder(
            role_admin="role_admin",
            role_backup="role_backup",
            role_ddl="role_ddl",
            role_stats="role_stats",
            role_reader="role_reader",
            role_writer="role_writer",
        )

        try:
            query = builder.build_instance_auth_roles_query()
            _____ = executor.execute_sql(query)

            executor.execute_sql("CREATE DATABASE IF NOT EXISTS test")
            executor.execute_sql("GRANT SELECT ON test.* TO role_reader")
            executor.execute_sql("GRANT SELECT, INSERT, UPDATE, DELETE ON test.* TO role_writer")

            # Testing admin instance role #
            executor.execute_sql("DROP USER IF EXISTS admin_user")
            executor.execute_sql("CREATE USER admin_user IDENTIFIED BY 'password'")
            executor.execute_sql("GRANT role_admin TO admin_user")

            admin_executor = build_local_executor(
                username="admin_user",
                password="password",
            )

            admin_executor.execute_sql(self.DB_CREATE_QUERY)
            admin_executor.execute_sql(self.TABLE_CREATE_QUERY)
            admin_executor.execute_sql(self.TABLE_INSERT_QUERY)
            admin_executor.execute_sql(self.TABLE_SELECT_QUERY)

            # Testing writer instance role #
            executor.execute_sql("DROP USER IF EXISTS writer_user")
            executor.execute_sql("CREATE USER writer_user IDENTIFIED BY 'password'")
            executor.execute_sql("GRANT role_writer TO writer_user")

            writer_executor = build_local_executor(
                username="writer_user",
                password="password",
            )

            with pytest.raises(ExecutionError):
                writer_executor.execute_sql(self.DB_CREATE_QUERY)
            with pytest.raises(ExecutionError):
                writer_executor.execute_sql(self.TABLE_CREATE_QUERY)

            writer_executor.execute_sql(self.TABLE_INSERT_QUERY)
            writer_executor.execute_sql(self.TABLE_SELECT_QUERY)

            # Testing reader instance role #
            executor.execute_sql("DROP USER IF EXISTS reader_user")
            executor.execute_sql("CREATE USER reader_user IDENTIFIED BY 'password'")
            executor.execute_sql("GRANT role_reader TO reader_user")

            reader_executor = build_local_executor(
                username="reader_user",
                password="password",
            )

            with pytest.raises(ExecutionError):
                reader_executor.execute_sql(self.DB_CREATE_QUERY)
            with pytest.raises(ExecutionError):
                reader_executor.execute_sql(self.TABLE_CREATE_QUERY)
            with pytest.raises(ExecutionError):
                reader_executor.execute_sql(self.TABLE_INSERT_QUERY)

            reader_executor.execute_sql(self.TABLE_SELECT_QUERY)
        finally:
            self._delete_role(executor, Role("role_admin"))
            self._delete_role(executor, Role("role_backup"))
            self._delete_role(executor, Role("role_ddl"))
            self._delete_role(executor, Role("role_stats"))
            self._delete_role(executor, Role("role_reader"))
            self._delete_role(executor, Role("role_writer"))

    def test_database_admin_role_query(self, executor: LocalExecutor):
        """Test the creation of a database admin role."""
        builder = CharmAuthorizationQueryBuilder(
            role_admin="role_admin",
            role_backup="role_backup",
            role_ddl="role_ddl",
            role_stats="role_stats",
            role_reader="role_reader",
            role_writer="role_writer",
        )

        try:
            executor.execute_sql("CREATE DATABASE IF NOT EXISTS test")

            query = builder.build_database_admin_role_query("test_db_admin", "test")
            _____ = executor.execute_sql(query)

            executor.execute_sql("DROP USER IF EXISTS db_admin_user")
            executor.execute_sql("CREATE USER db_admin_user IDENTIFIED BY 'password'")
            executor.execute_sql("GRANT test_db_admin TO db_admin_user")

            admin_executor = build_local_executor(
                username="db_admin_user",
                password="password",
            )

            admin_executor.execute_sql(self.DB_CREATE_QUERY)
            admin_executor.execute_sql(self.TABLE_CREATE_QUERY)
            admin_executor.execute_sql(self.TABLE_INSERT_QUERY)
            admin_executor.execute_sql(self.TABLE_SELECT_QUERY)
        finally:
            self._delete_role(executor, Role("test_db_admin"))
