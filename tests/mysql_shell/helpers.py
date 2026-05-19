# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os
import threading
import time
from contextlib import contextmanager

from mysql_shell.executors import LocalExecutor
from mysql_shell.models import ConnectionDetails

TEST_CLUSTER_NAME = "test-cluster"
TEST_CLUSTER_HOST = "0.0.0.0"
TEST_CLUSTER_PORT = "3306"


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


@contextmanager
def temp_process(query: str):
    """Context manager to run a piece of code with a background process."""
    executor = build_local_executor(
        username=os.environ["MYSQL_USERNAME"],
        password=os.environ["MYSQL_PASSWORD"],
    )

    thread = threading.Thread(target=executor.execute_sql, args=[query])

    try:
        thread.start()
        time.sleep(1)
        yield
    finally:
        thread.join()
