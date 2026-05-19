# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod
from typing import Sequence

from ...models import LogType


class BaseLoggingQueryBuilder(ABC):
    """Base class for all the logging query builders."""

    @abstractmethod
    def build_logs_flushing_query(self, logs: Sequence[LogType] | None) -> str:
        """Builds the logs flushing query."""
        raise NotImplementedError()
