# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from enum import Enum


class LogType(str, Enum):
    """MySQL log types.

    https://dev.mysql.com/doc/refman/8.0/en/flush.html#flush-logs
    """

    BINARY = "BINARY"
    ENGINE = "ENGINE"
    ERROR = "ERROR"
    GENERAL = "GENERAL"
    RELAY = "RELAY"
    SLOW = "SLOW"


class VariableScope(str, Enum):
    """MySQL variable scopes.

    https://dev.mysql.com/doc/refman/8.0/en/set-variable.html
    """

    GLOBAL = "GLOBAL"
    SESSION = "SESSION"
