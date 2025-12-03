# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from ..quoting import StringQueryQuoter
from .base import BaseLockingQueryBuilder


class CharmLockingQueryBuilder(BaseLockingQueryBuilder):
    """Charm locking query builder."""

    INSTANCE_ADDITION_TASK = "unit-add"
    INSTANCE_REMOVAL_TASK = "unit-teardown"

    TASKS = [
        INSTANCE_ADDITION_TASK,
        INSTANCE_REMOVAL_TASK,
    ]

    def __init__(self, table_schema: str, table_name: str):
        """Initialize the query builder."""
        self._quoter = StringQueryQuoter()
        self._table = "{table_schema}.{table_name}".format(
            table_schema=self._quoter.quote_identifier(table_schema),
            table_name=self._quoter.quote_identifier(table_name),
        )

    def build_table_creation_query(self) -> str:
        """Builds the locking table creation query."""
        create_query = (
            "CREATE TABLE IF NOT EXISTS {table} ( "
            "    task VARCHAR(20), "
            "    executor VARCHAR(20), "
            "    status VARCHAR(20), "
            "    PRIMARY KEY(task) "
            ")"
        )
        insert_query = (
            "INSERT INTO {table} (task, executor, status) "
            "VALUES ('{task}', '', 'not-started') "
            "ON DUPLICATE KEY UPDATE "
            "    executor = '', "
            "    status = 'not-started'"
        )

        create_queries = [create_query.format(table=self._table)]
        insert_queries = [insert_query.format(table=self._table, task=task) for task in self.TASKS]

        return ";".join((
            *create_queries,
            *insert_queries,
        ))

    def build_fetch_acquired_query(self, task: str) -> str:
        """Builds the acquired lock fetch query."""
        query = "SELECT executor FROM {table} WHERE task = {task} AND status = {status}"

        return query.format(
            table=self._table,
            task=self._quoter.quote_value(task),
            status=self._quoter.quote_value("in-progress"),
        )

    def build_acquire_query(self, task: str, instance: str) -> str:
        """Builds the lock acquiring query."""
        if task not in self.TASKS:
            raise ValueError("Task not supported")

        query = (
            "UPDATE {table} "
            "SET status = {status}, executor = {instance} "
            "WHERE task = {task} AND executor = ''"
        )

        return query.format(
            table=self._table,
            task=self._quoter.quote_value(task),
            instance=self._quoter.quote_value(instance),
            status=self._quoter.quote_value("in-progress"),
        )

    def build_release_query(self, task: str, instance: str) -> str:
        """Builds the lock releasing query."""
        if task not in self.TASKS:
            raise ValueError(f"Task not supported")

        query = (
            "UPDATE {table} "
            "SET status = {status}, executor = '' "
            "WHERE task = {task} AND executor = {instance}"
        )

        return query.format(
            table=self._table,
            task=self._quoter.quote_value(task),
            instance=self._quoter.quote_value(instance),
            status=self._quoter.quote_value("not-started"),
        )
