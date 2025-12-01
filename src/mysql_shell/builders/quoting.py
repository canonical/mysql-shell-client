# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import Any


class StringQueryQuoter:
    """Class to escape and quote MySQL query input parameters."""

    @staticmethod
    def escape(value: Any) -> Any:
        """Escapes a string that can be used in a SQL statement.

        This function will only be used in the context of MySQL Shell,
        so the recommended way to deal with SQL injection attacks,
        (using parametrized queries) is not available.

        The code has been copied from the mysql-connector Python package.
        https://github.com/mysql/mysql-connector-python/blob/8.0.33/lib/mysql/connector/conversion.py#L174-L201
        """
        if isinstance(value, (bytes, bytearray)):
            value = value.replace(b"\\", b"\\\\")
            value = value.replace(b"\n", b"\\n")
            value = value.replace(b"\r", b"\\r")
            value = value.replace(b"\140", b"\134\140")  # tick quote
            value = value.replace(b"\047", b"\134\047")  # single quotes
            value = value.replace(b"\042", b"\134\042")  # double quotes
            value = value.replace(b"\032", b"\134\032")  # for Win32
        elif isinstance(value, str):
            value = value.replace("\\", "\\\\")
            value = value.replace("\n", "\\n")
            value = value.replace("\r", "\\r")
            value = value.replace("\140", "\134\140")  # tick quote
            value = value.replace("\047", "\134\047")  # single quotes
            value = value.replace("\042", "\134\042")  # double quotes
            value = value.replace("\032", "\134\032")  # for Win32

        return value

    def quote_value(self, value: str) -> str:
        """Quotes the provided value."""
        return f"'{self.escape(value)}'"

    def quote_identifier(self, name: str) -> str:
        """Quotes the provided identifier name."""
        return f"`{self.escape(name)}`"
