# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.


class ExecutionError(RuntimeError):
    """MySQL shell execution error."""

    # The context attribute is overridden so passwords
    # are not logged in when showing the traceback
    # of the previously raised exception
    __context__ = None
