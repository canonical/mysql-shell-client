# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import re
import subprocess
from typing import Generator

from ..models import ConnectionDetails
from .base import BaseExecutor
from .errors import ExecutionError


class LocalExecutor(BaseExecutor):
    """Local executor for the MySQL Shell."""

    def __init__(self, conn_details: ConnectionDetails, shell_path: str):
        """Initialize the executor."""
        super().__init__(conn_details, shell_path)

    def _common_args(self) -> list[str]:
        """Return the list of common arguments."""
        return [
            self._shell_path,
            "--json=raw",
            "--save-passwords=never",
            "--passwords-from-stdin",
        ]

    def _connection_args(self) -> list[str]:
        """Return the list of connection arguments."""
        if self._conn_details.socket:
            return [
                f"--socket={self._conn_details.socket}",
                f"--user={self._conn_details.username}",
            ]
        else:
            return [
                f"--host={self._conn_details.host}",
                f"--port={self._conn_details.port}",
                f"--user={self._conn_details.username}",
            ]

    def _parse_error(self, output: str) -> dict:
        """Parse the execution error."""
        error = next(self._iter_output(output, "error"), None)
        if not error:
            error = {}

        return error

    def _parse_output_py(self, output: str) -> str:
        """Parse the Python execution output."""
        result = next(self._iter_output(output, "info"), None)
        if not result:
            result = "{}"

        return result

    def _parse_output_sql(self, output: str) -> list:
        """Parse the SQL execution output."""
        result = next(self._iter_output(output, "rows"), None)
        if not result:
            result = []

        return result

    @staticmethod
    def _iter_output(output: str, key: str) -> Generator:
        """Iterates over the log lines in reversed order."""
        logs = output.split("\n")

        # MySQL Shell always prints prompts and warnings first
        for log in reversed(logs):
            if not log:
                continue

            log = json.loads(log)
            val = log.get(key)
            if not isinstance(val, str) or val.strip():
                yield val

    @staticmethod
    def _strip_password(error: subprocess.SubprocessError):
        """Strip passwords from SQL scripts."""
        if not hasattr(error, "cmd"):
            return error

        password_pattern = re.compile("(?<=IDENTIFIED BY ')[^']+(?=')")
        password_replace = "*****"

        for index, value in enumerate(error.cmd):
            if "IDENTIFIED BY" in value:
                error.cmd[index] = re.sub(password_pattern, password_replace, value)

        return error

    def check_connection(self) -> None:
        """Check the connection."""
        command = [
            *self._common_args(),
            *self._connection_args(),
        ]

        try:
            subprocess.check_output(
                command,
                input=self._conn_details.password,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            err = self._parse_error(exc.output)
            raise ExecutionError(err)
        except subprocess.TimeoutExpired:
            raise ExecutionError()

    def execute_py(self, script: str, *, timeout: int | None = None) -> str:
        """Execute a Python script.

        Arguments:
            script: Python script to execute
            timeout: Optional timeout seconds

        Returns:
            String with the output of the MySQL Shell command.
            The output cannot be parsed to JSON, as the output depends on the script
        """
        # Prepend every Python command with useWizards=False, to disable interactive mode.
        # Cannot be set on command line as it conflicts with --passwords-from-stdin.
        script = "shell.options.set('useWizards', False)\n" + script

        command = [
            *self._common_args(),
            *self._connection_args(),
            "--py",
            "--execute",
            script,
        ]

        try:
            output = subprocess.check_output(
                command,
                timeout=timeout,
                input=self._conn_details.password,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            err = self._parse_error(exc.output)
            raise ExecutionError(err)
        except subprocess.TimeoutExpired:
            raise ExecutionError()
        else:
            return self._parse_output_py(output)

    def execute_sql(self, script: str, *, timeout: int | None = None) -> list[dict]:
        """Execute a SQL script.

        Arguments:
            script: SQL script to execute
            timeout: Optional timeout seconds

        Returns:
            List of dictionaries, one per returned row
        """
        command = [
            *self._common_args(),
            *self._connection_args(),
            "--sql",
            "--execute",
            script,
        ]

        try:
            output = subprocess.check_output(
                command,
                timeout=timeout,
                input=self._conn_details.password,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            err = self._parse_error(exc.output)
            exc = self._strip_password(exc)
            raise ExecutionError(err) from exc
        except subprocess.TimeoutExpired as exc:
            exc = self._strip_password(exc)
            raise ExecutionError() from exc
        else:
            return self._parse_output_sql(output)
