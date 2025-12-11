# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os
import threading
import time
from contextlib import contextmanager
from typing import Any, Generator

from mysql_shell.executors import LocalExecutor
from mysql_shell.models import ConnectionDetails, VariableScope

TEST_CLUSTER_NAME = "test-cluster"


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


@contextmanager
def temp_variable(scope: VariableScope, name: str, new_value: Any) -> Generator:
    """Context manager to run a piece of code with a variable changed."""
    executor = build_local_executor(
        username=os.environ.get("MYSQL_USERNAME"),
        password=os.environ.get("MYSQL_PASSWORD"),
    )

    set_query = "SET @@{scope}.{name} = {value}"
    get_query = "SELECT @@{scope}.{name} AS {name}"
    get_query = get_query.format(scope=scope.value, name=name)

    old_value = executor.execute_sql(get_query)[0][name]
    old_value = f"'{old_value}'" if isinstance(old_value, str) else old_value
    new_value = f"'{new_value}'" if isinstance(new_value, str) else new_value

    try:
        set_query_new = set_query.format(scope=scope.value, name=name, value=new_value)
        executor.execute_sql(set_query_new)
        yield
    finally:
        set_query_old = set_query.format(scope=scope.value, name=name, value=old_value)
        executor.execute_sql(set_query_old)
