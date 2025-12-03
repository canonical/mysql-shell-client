# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from mysql_shell.builders import CharmLockingQueryBuilder
from mysql_shell.executors import LocalExecutor

from ...helpers import build_local_executor


@pytest.mark.integration
class TestCharmLockingQueryBuilder:
    """Class to group all the CharmLockingQueryBuilder tests."""

    @pytest.fixture(scope="class")
    def executor(self):
        """Local executor fixture."""
        return build_local_executor(
            username=os.environ["MYSQL_USERNAME"],
            password=os.environ["MYSQL_PASSWORD"],
        )

    @staticmethod
    def _fetch_lock_instance(executor: LocalExecutor, task: str):
        """Fetches the instance holding a task lock."""
        query = (
            "SELECT executor "
            "FROM mysql.locking "
            "WHERE task = '{task_name}' AND status = 'in-progress'"
        )
        query = query.format(task_name=task)
        rows = executor.execute_sql(query)

        return next((row["executor"] for row in rows), None)

    def test_table_creation_query(self, executor: LocalExecutor):
        """Test the creation of a locking table."""
        builder = CharmLockingQueryBuilder("mysql", "locking")

        query = builder.build_table_creation_query()
        _____ = executor.execute_sql(query)

        tables = executor.execute_sql(
            "SELECT * "
            "FROM information_schema.tables "
            "WHERE table_schema = 'mysql' AND table_name = 'locking'"
        )
        locks = executor.execute_sql(
            "SELECT COUNT(*) FROM mysql.locking WHERE status = 'not-started'"
        )

        assert tables
        assert locks
        assert locks[0]["COUNT(*)"] == len(CharmLockingQueryBuilder.TASKS)

    def test_fetch_acquired_lock_query(self, executor: LocalExecutor):
        """Test the fetching for acquired table locks."""
        builder = CharmLockingQueryBuilder("mysql", "locking")
        task = CharmLockingQueryBuilder.INSTANCE_ADDITION_TASK
        query = builder.build_fetch_acquired_query(task)

        locks = executor.execute_sql(query)
        assert len(locks) == 0

        try:
            acquire_query = builder.build_acquire_query(task, "mysql-1")
            executor.execute_sql(acquire_query)

            locks = executor.execute_sql(query)
            assert len(locks) == 1
        finally:
            release_query = builder.build_release_query(task, "mysql-1")
            executor.execute_sql(release_query)

    def test_acquire_lock_query(self, executor: LocalExecutor):
        """Test the acquiring of the table lock."""
        builder = CharmLockingQueryBuilder("mysql", "locking")
        task = CharmLockingQueryBuilder.INSTANCE_ADDITION_TASK

        acquire_query = builder.build_acquire_query(task, "mysql-1")
        executor.execute_sql(acquire_query)

        acquire_query = builder.build_acquire_query(task, "mysql-2")
        executor.execute_sql(acquire_query)

        assert self._fetch_lock_instance(executor, task) == "mysql-1"

    def test_release_lock_query(self, executor: LocalExecutor):
        """Test the releasing of the table lock."""
        builder = CharmLockingQueryBuilder("mysql", "locking")
        task = CharmLockingQueryBuilder.INSTANCE_ADDITION_TASK

        release_query = builder.build_release_query(task, "mysql-1")
        executor.execute_sql(release_query)

        assert self._fetch_lock_instance(executor, task) is None
