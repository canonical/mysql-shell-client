# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os
from contextlib import contextmanager
from typing import Any

import pytest

from mysql_shell.models import VariableScope


@pytest.fixture(scope="session")
def temp_variable(build_local_executor):
    """Factory fixture returning a context manager that temporarily changes a MySQL variable."""

    @contextmanager
    def _temp_variable(scope: VariableScope, name: str, new_value: Any):
        executor = build_local_executor(
            username=os.environ.get("MYSQL_USERNAME", ""),
            password=os.environ.get("MYSQL_PASSWORD", ""),
        )

        set_query = "SET @@{scope}.{name} = {value}"
        get_query = "SELECT @@{scope}.{name} AS {name}"
        get_query = get_query.format(scope=scope.value, name=name)

        old_value = executor.execute_sql(get_query)[0][name]
        old_value = f"'{old_value}'" if isinstance(old_value, str) else old_value
        new_value_fmt = f"'{new_value}'" if isinstance(new_value, str) else new_value

        try:
            set_query_new = set_query.format(scope=scope.value, name=name, value=new_value_fmt)
            executor.execute_sql(set_query_new)
            yield
        finally:
            set_query_old = set_query.format(scope=scope.value, name=name, value=old_value)
            executor.execute_sql(set_query_old)

    return _temp_variable
