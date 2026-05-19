# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os
from contextlib import suppress

import pytest

from ..helpers import (
    TEST_CLUSTER_HOST,
    TEST_CLUSTER_NAME,
    TEST_CLUSTER_PORT,
    build_local_executor,
)

_GTID_MODES_ORDERED = (
    "OFF",
    "OFF_PERMISSIVE",
    "ON_PERMISSIVE",
    "ON",
)


def _create_cluster() -> None:
    """Creates InnoDB cluster."""
    executor = build_local_executor(
        username=os.environ["MYSQL_USERNAME"],
        password=os.environ["MYSQL_PASSWORD"],
        host=TEST_CLUSTER_HOST,
        port=TEST_CLUSTER_PORT,
    )

    with suppress(Exception):
        executor.execute_py(f"dba.create_cluster('{TEST_CLUSTER_NAME}')")


def _config_instance(instance_address: str, instance_port: str) -> None:
    """Configs as instance before joining a InnoDB cluster."""
    executor = build_local_executor(
        username=os.environ["MYSQL_USERNAME"],
        password=os.environ["MYSQL_PASSWORD"],
        host=instance_address,
        port=instance_port,
    )

    executor.execute_sql("SET @@GLOBAL.enforce_gtid_consistency = 'ON'")

    gtid_mode = executor.execute_sql("SELECT @@GLOBAL.gtid_mode AS gtid_mode")
    gtid_mode = gtid_mode[0]["gtid_mode"]
    gtid_mode_index = _GTID_MODES_ORDERED.index(gtid_mode)

    for mode in _GTID_MODES_ORDERED[gtid_mode_index:]:
        executor.execute_sql(f"SET @@GLOBAL.gtid_mode = '{mode}'")


def _join_instance(instance_address: str, instance_port: str) -> None:
    """Joins an instance to the testing InnoDB cluster."""
    executor = build_local_executor(
        username=os.environ["MYSQL_USERNAME"],
        password=os.environ["MYSQL_PASSWORD"],
        host=TEST_CLUSTER_HOST,
        port=TEST_CLUSTER_PORT,
    )

    executor.execute_py(
        "\n".join((
            f"cluster = dba.get_cluster('{TEST_CLUSTER_NAME}')",
            f"cluster.add_instance("
            f"  instance='{instance_address}:{instance_port}',"
            f"  options={{'recoveryMethod': 'incremental'}},"
            f")",
        )),
    )


@pytest.fixture(scope="session", autouse=True)
def initialize_cluster():
    """Initializes InnoDB cluster in an idempotent way."""
    _config_instance(instance_address=TEST_CLUSTER_HOST, instance_port="3306")
    _config_instance(instance_address=TEST_CLUSTER_HOST, instance_port="3307")
    _config_instance(instance_address=TEST_CLUSTER_HOST, instance_port="3308")

    _create_cluster()
    _join_instance(instance_address=TEST_CLUSTER_HOST, instance_port="3307")
    _join_instance(instance_address=TEST_CLUSTER_HOST, instance_port="3308")
