# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from mysql_shell.executors import LocalExecutor
from mysql_shell.models import ConnectionDetails


@pytest.fixture(scope="session")
def build_local_executor():
    """Factory fixture that returns a callable to build a LocalExecutor."""

    def _build(username: str, password: str, host: str = "0.0.0.0", port: str = "3306"):
        conn_details = ConnectionDetails(
            username=username,
            password=password,
            host=host,
            port=port,
        )
        return LocalExecutor(
            conn_details=conn_details,
            shell_path=os.environ["MYSQL_SHELL_PATH"],
        )

    return _build
