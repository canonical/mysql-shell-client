# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os
from contextlib import suppress

import pytest

from ..helpers import build_local_executor

_GTID_MODES_ORDERED = (
    "OFF",
    "OFF_PERMISSIVE",
    "ON_PERMISSIVE",
    "ON",
)


@pytest.fixture(scope="session", autouse=True)
def initialize_cluster():
    """Initializes InnoDB cluster in an idempotent way."""
    executor = build_local_executor(
        username=os.environ["MYSQL_USERNAME"],
        password=os.environ["MYSQL_PASSWORD"],
    )

    # This variable is MySQL 8.0 specific
    with suppress(Exception):
        executor.execute_sql("SET @@GLOBAL.binlog_transaction_dependency_tracking = 'WRITESET'")

    executor.execute_sql("SET @@GLOBAL.enforce_gtid_consistency = 'ON'")
    executor.execute_sql("SET @@GLOBAL.server_id = 1")

    gtid_mode = executor.execute_sql("SELECT @@GLOBAL.gtid_mode AS gtid_mode")
    gtid_mode = gtid_mode[0]["gtid_mode"]
    gtid_mode_index = _GTID_MODES_ORDERED.index(gtid_mode)

    for mode in _GTID_MODES_ORDERED[gtid_mode_index:]:
        executor.execute_sql(f"SET @@GLOBAL.gtid_mode = '{mode}'")

    with suppress(Exception):
        executor.execute_py("dba.create_cluster('my-cluster')")
