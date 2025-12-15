# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import Any


class ExecutionError(RuntimeError):
    """MySQL shell execution error."""

    def __init__(self, message: Any | None = None):
        """Initialize the error."""
        if isinstance(message, dict):
            message = message.get("message")

        super().__init__(message)
