# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod


class BaseLockingQueryBuilder(ABC):
    """Base class for all the locking query builders."""

    @abstractmethod
    def build_table_creation_query(self) -> str:
        """Builds the locking table creation query."""
        raise NotImplementedError()

    @abstractmethod
    def build_fetch_acquired_query(self, task: str) -> str:
        """Builds the acquired lock check query."""
        raise NotImplementedError()

    @abstractmethod
    def build_acquire_query(self, task: str, instance: str) -> str:
        """Builds the lock acquiring query."""
        raise NotImplementedError()

    @abstractmethod
    def build_release_query(self, task: str, instance: str) -> str:
        """Builds the lock releasing query."""
        raise NotImplementedError()
