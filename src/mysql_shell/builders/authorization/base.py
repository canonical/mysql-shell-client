# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod


class BaseAuthorizationQueryBuilder(ABC):
    """Base class for authorization query builders."""

    @abstractmethod
    def build_instance_auth_roles_query(self) -> str:
        """Builds the instance roles creation query."""
        raise NotImplementedError()

    @abstractmethod
    def build_instance_router_role_query(self, rolename: str) -> str:
        """Builds the instance router role creation query."""
        raise NotImplementedError()

    @abstractmethod
    def build_database_admin_role_query(self, rolename: str, database: str) -> str:
        """Builds the database admin role creation query."""
        raise NotImplementedError()
