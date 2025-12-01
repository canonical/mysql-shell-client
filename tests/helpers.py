# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

from mysql_shell.executors import LocalExecutor
from mysql_shell.models import ConnectionDetails


def build_local_executor(username: str, password: str, host: str = "0.0.0.0", port: str = "3306"):
    """Build a local executor for testing."""
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
