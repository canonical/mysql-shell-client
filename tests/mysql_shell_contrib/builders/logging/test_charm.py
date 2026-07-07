# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from helpers import build_local_executor
from mysql_shell.executors import LocalExecutor
from mysql_shell.models import LogType
from mysql_shell_contrib.builders import CharmLoggingQueryBuilder


@pytest.mark.integration
class TestCharmLoggingQueryBuilder:
    """Class to group all the CharmLoggingQueryBuilder tests."""

    @pytest.fixture(scope="class")
    def executor(self):
        """Local executor fixture."""
        return build_local_executor(
            username=os.environ["MYSQL_USERNAME"],
            password=os.environ["MYSQL_PASSWORD"],
        )

    def test_logs_flushing_query(self, executor: LocalExecutor):
        """Test the flushing of logs."""
        builder = CharmLoggingQueryBuilder()

        query = builder.build_logs_flushing_query([])
        _____ = executor.execute_sql(query)

        query = builder.build_logs_flushing_query([LogType.GENERAL, LogType.ERROR])
        _____ = executor.execute_sql(query)
