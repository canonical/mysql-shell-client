# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import os

import pytest

from mysql_shell.executors import LocalExecutor
from mysql_shell.executors.errors import ExecutionError

from ..helpers import build_local_executor


@pytest.mark.integration
class TestLocalExecutor:
    """Class to group all the LocalExecutor tests."""

    @pytest.fixture(scope="class")
    def executor(self):
        """Local executor fixture."""
        return build_local_executor(
            username=os.environ["MYSQL_USERNAME"],
            password=os.environ["MYSQL_PASSWORD"],
        )

    def test_check_connection(self, executor: LocalExecutor):
        """Check the connection."""
        executor.check_connection()

    def test_check_connection_error(self, executor: LocalExecutor):
        """Check the connection when there is an error."""
        executor = build_local_executor(
            username="wrong_username",
            password="wrong_password",
        )

        try:
            executor.check_connection()
        except ExecutionError as e:
            assert str(e) == str(None)

    def test_execute_py(self, executor: LocalExecutor):
        """Test the execution of Python scripts."""
        result = executor.execute_py("print('hello world')")
        assert isinstance(result, str)
        assert result == "hello world"

        result = executor.execute_py("a = 1")
        assert isinstance(result, str)
        result = json.loads(result)
        assert isinstance(result, dict)

    def test_execute_py_error(self, executor: LocalExecutor):
        """Test the execution of Python scripts when there is an error."""
        try:
            executor.execute_py("syntax")
        except ExecutionError as e:
            assert str(e) == "name 'syntax' is not defined"

        executor = build_local_executor(
            username="wrong_username",
            password="wrong_password",
        )

        try:
            executor.execute_py("pass")
        except ExecutionError as e:
            assert str(e) == str(None)

    def test_execute_sql(self, executor: LocalExecutor):
        """Test the execution of SQL scripts."""
        rows = executor.execute_sql("SELECT 1")
        assert isinstance(rows, list)
        assert rows[0]["1"]

        rows = executor.execute_sql("SELECT user FROM mysql.user")
        assert isinstance(rows, list)
        assert any(row["user"] == "root" for row in rows)

    def test_execute_sql_error(self, executor: LocalExecutor):
        """Test the execution of SQL scripts when there is an error."""
        try:
            executor.execute_sql("SELECT")
        except ExecutionError as e:
            assert str(e).startswith("You have an error in your SQL syntax")

        executor = build_local_executor(
            username="wrong_username",
            password="wrong_password",
        )

        try:
            executor.execute_sql("SELECT 1")
        except ExecutionError as e:
            assert str(e) == str(None)
