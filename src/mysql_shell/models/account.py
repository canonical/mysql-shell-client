# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import json
from dataclasses import dataclass


@dataclass
class Role:
    """MySQL role account."""

    rolename: str
    hostname: str = "%"

    @classmethod
    def from_row(cls, rolename: str, hostname: str):
        """Create a role account from a MySQL row."""
        return Role(
            rolename=rolename,
            hostname=hostname,
        )


@dataclass
class User:
    """MySQL user account."""

    username: str
    hostname: str = "%"
    attributes: dict | None = None

    @classmethod
    def from_row(cls, username: str, hostname: str, attributes: str | None):
        """Create a user account from a MySQL row."""
        if not attributes:
            attributes = "{}"

        return User(
            username=username,
            hostname=hostname,
            attributes=json.loads(attributes),
        )

    def serialize_attrs(self) -> str:
        """Serialize the user attributes."""
        if not self.attributes:
            return "{}"

        return json.dumps(self.attributes)
