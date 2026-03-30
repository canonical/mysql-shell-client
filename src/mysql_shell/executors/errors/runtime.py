# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.


class ExecutionError(RuntimeError):
    """MySQL shell execution error."""

    def __init__(self, message: str | None = None):
        """Initialize the error."""
        super().__init__(message)
