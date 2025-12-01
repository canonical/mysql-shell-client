# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod
from typing import Sequence

from ..models import ConnectionDetails


class BaseExecutor(ABC):
    """Base class for all MySQL Shell executors."""

    @property
    @abstractmethod
    def connection_details(self) -> ConnectionDetails:
        """Return the connection details."""
        raise NotImplementedError()

    @abstractmethod
    def check_connection(self) -> None:
        """Check the connection."""
        raise NotImplementedError()

    @abstractmethod
    def execute_py(self, script: str, *, timeout: int = 10) -> str:
        """Execute a Python script."""
        raise NotImplementedError()

    @abstractmethod
    def execute_sql(self, script: str, *, timeout: int = 10) -> Sequence[dict]:
        """Execute a SQL script."""
        raise NotImplementedError()
