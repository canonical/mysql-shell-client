# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import json


class ExecutionError(RuntimeError):
    """MySQL shell execution error."""

    def __init__(self, message: str | None = None):
        """Initialize the error."""
        if not message:
            return

        if not message.startswith("MySQL Error"):
            message = json.loads(message)
            message = message.get("error") if message else message
            message = message.get("message") if message else message

        super().__init__(message)
