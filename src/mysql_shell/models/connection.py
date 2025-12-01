# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from dataclasses import dataclass


@dataclass
class ConnectionDetails:
    """MySQL connection details."""

    username: str
    password: str
    host: str = ""
    port: str = ""
    socket: str = ""

    def __post_init__(self) -> None:
        """Validates that the connection details are correct."""
        if (not self.host or not self.port) and not self.socket:
            raise ValueError("Connection details must not be empty")
        if (self.host or self.port) and self.socket:
            raise ValueError("Connection details must not be state both TCP and socket values")
