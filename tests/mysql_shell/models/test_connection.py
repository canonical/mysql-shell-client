# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from mysql_shell.models import ConnectionDetails


@pytest.mark.unit
class TestConnectionDetails:
    """Class to group all the ConnectionDetails tests."""

    def test_valid_init(self):
        """Test the correct initialization."""
        assert ConnectionDetails(
            username="test",
            password="test",
            host="localhost",
            port="3306",
        )
        assert ConnectionDetails(
            username="test",
            password="test",
            socket="/var/snap/mysql/20/run/mysqld.sock",
        )

    def test_invalid_init(self):
        """Test the incorrect initialization."""
        with pytest.raises(ValueError):
            ConnectionDetails(
                username="test",
                password="test",
            )
        with pytest.raises(ValueError):
            ConnectionDetails(
                username="test",
                password="test",
                host="localhost",
                port="3306",
                socket="/var/snap/mysql/20/run/mysqld.sock",
            )
