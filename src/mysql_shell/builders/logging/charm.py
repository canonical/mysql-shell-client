# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import Sequence

from ...models import LogType
from ..quoting import StringQueryQuoter
from .base import BaseLoggingQueryBuilder


class CharmLoggingQueryBuilder(BaseLoggingQueryBuilder):
    """Charm logging query builder."""

    def __init__(self):
        """Initialize the query builder."""
        self._quoter = StringQueryQuoter()

    def build_logs_flushing_query(self, logs: Sequence[LogType] | None = None) -> str:
        """Builds the logs flushing query.

        Arguments:
            logs: a sequence of LogTypes to flush. If None, flush all
        """
        binlog_query = "SET @@SESSION.sql_log_bin = {value}"

        if not logs:
            flush_query = "FLUSH LOGS"
        else:
            flush_query = "FLUSH {log} LOGS"
            flush_query = ";".join(flush_query.format(log=log.value) for log in logs)

        return ";".join((
            binlog_query.format(value=self._quoter.quote_value("OFF")),
            flush_query,
            binlog_query.format(value=self._quoter.quote_value("ON")),
        ))
