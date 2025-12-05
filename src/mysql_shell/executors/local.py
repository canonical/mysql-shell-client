# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import subprocess

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

    @staticmethod
    def _parse_output(output: str) -> str | dict:
        """Parse the error message."""
        # MySQL Shell always prompts for the user password
        output = output.split("\n")[1]

        try:
            message = json.loads(output)
        except json.JSONDecodeError:
            return output
        else:
            return message

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
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise ExecutionError(f"MySQL Shell failed: {self._parse_output(exc.output)}")
        except subprocess.TimeoutExpired:
            raise ExecutionError(f"MySQL Shell timed out")

    def execute_py(self, script: str, *, timeout: int = 10) -> str:
        """Execute a Python script.

        Arguments:
            script: Python script to execute
            timeout: Optional timeout seconds

        Returns:
            String with the output of the MySQL Shell command.
            The output cannot be parsed to JSON, as the output depends on the script
        """
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
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            error = self._parse_output(exc.output)
            error = error.get("error")
            raise ExecutionError(f"MySQL Shell failed: {error}")
        except subprocess.TimeoutExpired:
            raise ExecutionError(f"MySQL Shell timed out")
        else:
            result = self._parse_output(output)
            result = result.get("info", "")
            return result.strip()

    def execute_sql(self, script: str, *, timeout: int = 10) -> list[dict]:
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
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            error = self._parse_output(exc.output)
            error = error.get("error")
            error = error.get("message")
            raise ExecutionError(f"MySQL Shell failed: {error}")
        except subprocess.TimeoutExpired:
            raise ExecutionError(f"MySQL Shell timed out")
        else:
            result = self._parse_output(output)
            result = result.get("rows", [])
            return result
