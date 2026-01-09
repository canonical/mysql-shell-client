# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod
from typing import Sequence


class BaseLoggingQueryBuilder(ABC):
    """Base class for all the logging query builders."""

    @abstractmethod
    def build_logs_flushing_query(self, logs: Sequence[str] | None) -> str:
        """Builds the logs flushing query."""
        raise NotImplementedError()
