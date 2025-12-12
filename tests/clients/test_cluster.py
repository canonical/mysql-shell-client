# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from mysql_shell.clients import MySQLClusterClient
from mysql_shell.executors import LocalExecutor

from ..helpers import (
    TEST_CLUSTER_NAME,
    build_local_executor,
)


@pytest.mark.integration
class TestClusterClient:
    """Class to group all the MySQLClusterClient tests."""

    @pytest.fixture(scope="class", autouse=True)
    def executor(self):
        """Local executor fixture."""
        return build_local_executor(
            username=os.environ["MYSQL_USERNAME"],
            password=os.environ["MYSQL_PASSWORD"],
        )

    @pytest.fixture(scope="class", autouse=True)
    def client(self, executor: LocalExecutor):
        """MySQL Cluster client fixture."""
        return MySQLClusterClient(executor)

    @staticmethod
    def _get_member_address(client: MySQLClusterClient) -> str:
        """Get the member address."""
        query = (
            "SELECT CONCAT(member_host, ':', member_port) AS address "
            "FROM performance_schema.replication_group_members "
            "WHERE member_id = @@server_uuid"
        )

        rows = client._executor.execute_sql(query)
        host = rows[0]["address"]
        return host

    def test_fetch_cluster_status(self, client: MySQLClusterClient):
        """Test the fetching of the cluster status."""
        status = client.fetch_cluster_status(TEST_CLUSTER_NAME)
        assert status.get("defaultReplicaSet", {})
        assert status.get("defaultReplicaSet", {}).get("topology")

    def test_list_cluster_routers(self, client: MySQLClusterClient):
        """Test the listing of the cluster routers."""
        routers = client.list_cluster_routers(TEST_CLUSTER_NAME)
        routers = routers["routers"]
        assert len(routers) == 0

    def test_check_instance_before_cluster(self, client: MySQLClusterClient):
        """Test the checking of an instance config before joining a cluster."""
        assert client.check_instance_before_cluster()

    def test_update_instance_within_cluster(self, client: MySQLClusterClient):
        """Test the updating an instance config within a cluster."""
        address = self._get_member_address(client)

        try:
            client.update_instance_within_cluster(
                cluster_name=TEST_CLUSTER_NAME,
                instance_host="0.0.0.0",
                instance_port="3306",
                options={"label": "mysql-0"},
            )
        finally:
            client.update_instance_within_cluster(
                cluster_name=TEST_CLUSTER_NAME,
                instance_host="0.0.0.0",
                instance_port="3306",
                options={"label": f"{address}"},
            )
