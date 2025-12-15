# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod
from typing import Any, Sequence

from ..models import ConnectionDetails


class BaseExecutor(ABC):
    """Base class for all MySQL Shell executors."""

    def __init__(self, conn_details: ConnectionDetails, shell_path: str):
        """Initialize the executor."""
        self._conn_details = conn_details
        self._shell_path = shell_path

    @property
    def connection_details(self) -> ConnectionDetails:
        """Return the connection details."""
        return self._conn_details

    @abstractmethod
    def check_connection(self) -> None:
        """Check the connection."""
        raise NotImplementedError()

    @abstractmethod
    def execute_py(self, script: str, *, timeout: int | None = None) -> Any:
        """Execute a Python script."""
        raise NotImplementedError()

    @abstractmethod
    def execute_sql(self, script: str, *, timeout: int | None = None) -> Sequence[dict]:
        """Execute a SQL script."""
        raise NotImplementedError()
