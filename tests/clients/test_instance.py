# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from mysql_shell import VariableScope
from mysql_shell.builders import StringQueryQuoter
from mysql_shell.clients import MySQLInstanceClient
from mysql_shell.models.account import Role, User
from mysql_shell.models.statement import LogType

from ..helpers import build_local_executor


@pytest.mark.integration
class TestInstanceClient:
    """Class to group all the MySQLInstanceClient tests."""

    @pytest.fixture(scope="class")
    def client(self):
        """MySQL Instance client fixture."""
        quoter = StringQueryQuoter()
        executor = build_local_executor(
            username=os.environ["MYSQL_USERNAME"],
            password=os.environ["MYSQL_PASSWORD"],
        )

        return MySQLInstanceClient(executor, quoter)

    @staticmethod
    def _delete_user(client: MySQLInstanceClient, user: User):
        """Get the granted roles for a user."""
        query = "DROP USER IF EXISTS '{username}'@'{hostname}'"
        query = query.format(
            username=user.username,
            hostname=user.hostname,
        )

        client._executor.execute_sql(query)

    @staticmethod
    def _delete_role(client: MySQLInstanceClient, role: Role):
        """Get the granted roles for a user."""
        query = "DROP ROLE IF EXISTS '{rolename}'@'{hostname}'"
        query = query.format(
            rolename=role.rolename,
            hostname=role.hostname,
        )

        client._executor.execute_sql(query)

    @staticmethod
    def _get_granted_roles(client: MySQLInstanceClient, entity: User | Role):
        """Get the granted roles for a user."""
        query = (
            "SELECT from_user "
            "FROM mysql.role_edges "
            "WHERE to_user='{username}' AND to_host='{hostname}'"
        )

        query = query.format(
            username=entity.username if isinstance(entity, User) else entity.rolename,
            hostname=entity.hostname,
        )

        return [row["from_user"] for row in client._executor.execute_sql(query)]

    def test_create_instance_role_without_roles(self, client: MySQLInstanceClient):
        """Test the creation of an instance role."""
        role = Role("instance_role_create", "%")

        try:
            client.create_instance_role(role)
            roles = client.search_instance_roles(role.rolename)
            assert len(roles) > 0
        finally:
            self._delete_role(client, role)

    def test_create_instance_role_with_roles(self, client: MySQLInstanceClient):
        """Test the creation of an instance role."""
        role = Role("instance_role_create", "%")

        try:
            client.create_instance_role(role, ["root"])

            roles = client.search_instance_roles(role.rolename)
            assert len(roles) > 0

            roles_granted = self._get_granted_roles(client, role)
            assert len(roles_granted) > 0
            assert roles_granted[0] == "root"
        finally:
            self._delete_role(client, role)

    def test_create_instance_user_without_roles(self, client: MySQLInstanceClient):
        """Test the creation of an instance user."""
        user = User("instance_user_create", "%")

        try:
            client.create_instance_user(user, "password", [])
            users = client.search_instance_users(user.username)
            assert len(users) > 0
        finally:
            self._delete_user(client, user)

    def test_create_instance_user_with_roles(self, client: MySQLInstanceClient):
        """Test the creation of an instance user."""
        user = User("instance_user_create", "%")

        try:
            client.create_instance_user(user, "password", ["root"])

            users = client.search_instance_users(user.username)
            assert len(users) > 0

            roles_granted = self._get_granted_roles(client, user)
            assert len(roles_granted) > 0
            assert roles_granted[0] == "root"
        finally:
            self._delete_user(client, user)

    def test_delete_instance_user(self, client: MySQLInstanceClient):
        """Test the deletion of an instance user."""
        user = User("instance_user_delete", "%")

        try:
            client.create_instance_user(user, "password")
            client.delete_instance_user(user)

            users = client.search_instance_users(user.username)
            assert len(users) == 0
        finally:
            self._delete_user(client, user)

    def test_delete_instance_users(self, client: MySQLInstanceClient):
        """Test the deletion of a range of instance users."""
        user_1 = User("instance_user_delete_1", "%")
        user_2 = User("instance_user_delete_2", "%")

        try:
            client.create_instance_user(user_1, "password")
            client.create_instance_user(user_2, "password")

            users = client.search_instance_users("instance_user_delete_%")
            assert len(users) == 2

            client.delete_instance_users([user_1, user_2])

            users = client.search_instance_users("instance_user_delete_%")
            assert len(users) == 0
        finally:
            self._delete_user(client, user_1)
            self._delete_user(client, user_2)

    def test_update_instance_user(self, client: MySQLInstanceClient):
        """Test the updating of an instance user."""
        instance_user = User("instance_user_update", "%")

        try:
            client.create_instance_user(instance_user, "password")
            client.update_instance_user(instance_user, "password_new")

            executor = build_local_executor(instance_user.username, "password_new")
            executor.check_connection()
        finally:
            self._delete_user(client, instance_user)

    def test_flush_instance_logs(self, client: MySQLInstanceClient):
        """Test the flushing of a range of instance logs."""
        client.flush_instance_logs([])
        client.flush_instance_logs([LogType.GENERAL, LogType.ERROR])

    def test_get_cluster_instance_label(self, client: MySQLInstanceClient):
        """Test the fetching of the cluster instance label."""
        pass

    def test_get_cluster_instance_labels(self, client: MySQLInstanceClient):
        """Test the fetching of all the cluster instance labels."""
        pass

    def test_get_instance_replication_state(self, client: MySQLInstanceClient):
        """Test the fetching of the instance replication state."""
        pass

    def test_get_instance_replication_role(self, client: MySQLInstanceClient):
        """Test the fetching of the instance replication role."""
        pass

    def test_get_instance_variable(self, client: MySQLInstanceClient):
        """Test the fetching of an instance variable."""
        assert client.get_instance_variable(VariableScope.GLOBAL, "super_read_only") == 0

    def test_set_instance_variable(self, client: MySQLInstanceClient):
        """Test the fetching of an instance variable."""
        prev_value = client.get_instance_variable(VariableScope.GLOBAL, "max_connections")

        try:
            _ = client.set_instance_variable(VariableScope.GLOBAL, "max_connections", 100)
            v = client.get_instance_variable(VariableScope.GLOBAL, "max_connections")
            assert v == 100
        finally:
            client.set_instance_variable(VariableScope.GLOBAL, "max_connections", prev_value)

    def test_install_plugin(self, client: MySQLInstanceClient):
        """Test the installation of an instance plugin."""
        try:
            client.install_instance_plugin("auth_socket", "auth_socket.so")

            plugins = client.search_instance_plugins("%")
            assert len(plugins) == 1
            assert "auth_socket" in plugins
        finally:
            client.uninstall_instance_plugin("auth_socket")

    def test_search_instance_databases(self, client: MySQLInstanceClient):
        """Test the searching of instance databases given a name-pattern."""
        dbs = client.search_instance_databases("%")
        assert "mysql" in dbs
        assert "information_schema" in dbs
        assert "performance_schema" in dbs

        dbs = client.search_instance_databases("database_search")
        assert not dbs

    def test_search_instance_plugins(self, client: MySQLInstanceClient):
        """Test the searching of instance plugins given a name-pattern."""
        plugins = client.search_instance_plugins("%")
        assert len(plugins) == 0

    def test_search_instance_roles(self, client: MySQLInstanceClient):
        """Test the searching of instance roles given a name-pattern."""
        role = Role("instance_role_search", "%")

        try:
            client.create_instance_role(role)

            assert role in client.search_instance_roles("%")
            assert role not in client.search_instance_roles("unknown")
        finally:
            self._delete_role(client, role)

    def test_search_instance_users_without_attrs(self, client: MySQLInstanceClient):
        """Test the searching of instance users given a name-pattern."""
        user = User("instance_user_search", "%", {})

        try:
            client.create_instance_user(user, "password")

            assert user in client.search_instance_users("%")
            assert user not in client.search_instance_users("unknown")
        finally:
            self._delete_user(client, user)

    def test_search_instance_users_with_attrs(self, client: MySQLInstanceClient):
        """Test the searching of instance users given a name-pattern and attributes."""
        user = User("instance_user_search", "%", {"key": "val"})

        try:
            client.create_instance_user(user, "password")

            assert user in client.search_instance_users("%", {"key": "val"})
            assert user not in client.search_instance_users("%", {"key": "val_unknown"})
        finally:
            self._delete_user(client, user)

    def test_start_replication(self, client: MySQLInstanceClient):
        """Test the starting of group replication."""
        pass

    def test_stop_replication(self, client: MySQLInstanceClient):
        """Test the stopping of group replication."""
        pass
