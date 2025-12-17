# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from mysql_shell.builders import StringQueryQuoter
from mysql_shell.clients import MySQLInstanceClient
from mysql_shell.executors import LocalExecutor
from mysql_shell.models.account import Role, User
from mysql_shell.models.instance import InstanceRole, InstanceState
from mysql_shell.models.statement import LogType, VariableScope

from ..helpers import (
    TEST_CLUSTER_NAME,
    build_local_executor,
    temp_process,
)


@pytest.mark.integration
class TestInstanceClient:
    """Class to group all the MySQLInstanceClient tests."""

    @pytest.fixture(scope="class", autouse=True)
    def executor(self):
        """Local executor fixture."""
        return build_local_executor(
            username=os.environ["MYSQL_USERNAME"],
            password=os.environ["MYSQL_PASSWORD"],
        )

    @pytest.fixture(scope="class", autouse=True)
    def client(self, executor: LocalExecutor):
        """MySQL Instance client fixture."""
        return MySQLInstanceClient(executor, StringQueryQuoter())

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

        rows = client._executor.execute_sql(query)
        users = [row["from_user"] for row in rows]
        return users

    @staticmethod
    def _get_processes(client: MySQLInstanceClient, info: str):
        """Get the processes by statement."""
        query = (
            "SELECT processlist_id "
            "FROM performance_schema.threads "
            "WHERE processlist_info = '{info}'"
        )
        query = query.format(info=info)

        rows = client._executor.execute_sql(query)
        procs = [row["processlist_id"] for row in rows]
        return procs

    def test_check_work_ongoing(self, client: MySQLInstanceClient):
        """Test the checking of instance work."""
        assert not client.check_work_ongoing("%")

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

    def test_update_instance_user_password(self, client: MySQLInstanceClient):
        """Test the updating of an instance user password."""
        instance_user = User("instance_user_update", "%")

        try:
            client.create_instance_user(instance_user, password="password")
            client.update_instance_user(instance_user, password="password_new")

            executor = build_local_executor(instance_user.username, "password_new")
            executor.check_connection()
        finally:
            self._delete_user(client, instance_user)

    def test_update_instance_user_attributes(self, client: MySQLInstanceClient):
        """Test the updating of an instance user attributes."""
        old_attrs = {"key": "val_1"}
        new_attrs = {"key": "val_2"}

        instance_user = User("instance_user_update", "%", old_attrs)

        try:
            client.create_instance_user(instance_user, password="password")
            client.update_instance_user(instance_user, password="password", attrs=new_attrs)

            users = client.search_instance_users(instance_user.username)
            assert len(users) > 0
            assert users[0].attributes == new_attrs
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

    def test_get_cluster_labels(self, client: MySQLInstanceClient):
        """Test the fetching of all the cluster labels."""
        assert TEST_CLUSTER_NAME in client.get_cluster_labels()

    def test_get_instance_replication_state(self, client: MySQLInstanceClient):
        """Test the fetching of the instance replication state."""
        assert client.get_instance_replication_state() == InstanceState.ONLINE

    def test_get_instance_replication_role(self, client: MySQLInstanceClient):
        """Test the fetching of the instance replication role."""
        assert client.get_instance_replication_role() == InstanceRole.PRIMARY

    def test_get_instance_variable(self, client: MySQLInstanceClient):
        """Test the fetching of an instance variable."""
        assert client.get_instance_variable(VariableScope.GLOBAL, "super_read_only") == 0

    def test_set_instance_variable(self, client: MySQLInstanceClient):
        """Test the fetching of an instance variable."""
        var_name = "max_connections"
        var_value = 100

        client.set_instance_variable(VariableScope.GLOBAL, var_name, var_value)
        assert client.get_instance_variable(VariableScope.GLOBAL, var_name) == var_value

        var_name = "ssl_ca"
        var_value = "ca.pem"

        client.set_instance_variable(VariableScope.GLOBAL, var_name, var_value)
        assert client.get_instance_variable(VariableScope.GLOBAL, var_name) == var_value

    def test_install_plugin(self, client: MySQLInstanceClient):
        """Test the installation of an instance plugin."""
        plugins = client.search_instance_plugins("%")
        assert "auth_socket" not in plugins

        try:
            client.install_instance_plugin("auth_socket", "auth_socket.so")

            plugins = client.search_instance_plugins("%")
            assert "auth_socket" in plugins
        finally:
            client.uninstall_instance_plugin("auth_socket")

    def test_reload_instance_certs(self, client: MySQLInstanceClient):
        """Test the reloading of instance TLS certificates."""
        pass

    def test_search_instance_replication_members(self, client: MySQLInstanceClient):
        """Test the searching of instance replication members."""
        members = client.search_instance_replication_members()
        assert len(members) == 1

        primary_members = client.search_instance_replication_members([InstanceRole.PRIMARY], [])
        replica_members = client.search_instance_replication_members([InstanceRole.SECONDARY], [])
        assert len(primary_members) == 1
        assert len(replica_members) == 0

        online_members = client.search_instance_replication_members([], [InstanceState.ONLINE])
        offline_members = client.search_instance_replication_members([], [InstanceState.OFFLINE])
        assert len(online_members) == 1
        assert len(offline_members) == 0

    def test_search_instance_connections(self, client: MySQLInstanceClient):
        """Test the searching of instance connections given a name-pattern."""
        query = "DO SLEEP(10)"

        with temp_process(query):
            process_ids = self._get_processes(client, query)
            assert len(process_ids) == 1

            assert process_ids[0] in client.search_instance_connection_processes("%")
            assert process_ids[0] not in client.search_instance_connection_processes("search")

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
        assert "clone" in plugins
        assert "group_replication" in plugins

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

    def test_start_instance_replication(self, client: MySQLInstanceClient):
        """Test the starting of group replication."""
        pass

    def test_stop_instance_replication(self, client: MySQLInstanceClient):
        """Test the stopping of group replication."""
        pass

    def test_stop_instance_processes(self, client: MySQLInstanceClient):
        """Test the stopping of processes."""
        query = "DO SLEEP(10)"

        with temp_process(query):
            process_ids = self._get_processes(client, query)
            assert len(process_ids) == 1

            assert process_ids[0] in client.search_instance_connection_processes("%")
            client.stop_instance_processes(process_ids)
            assert process_ids[0] not in client.search_instance_connection_processes("%")
