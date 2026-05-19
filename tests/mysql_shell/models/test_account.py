# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from mysql_shell.models import User


@pytest.mark.unit
class TestUser:
    """Class to group all the User tests."""

    def test_serialize_empty_attrs(self):
        """Test the serialization of empty attributes."""
        user = User(
            username="test",
            hostname="localhost",
            attributes=None,
        )

        assert user.serialize_attrs() == "{}"

    def test_serialize_filled_attrs(self):
        """Test the serialization of filled attributes."""
        user = User(
            username="test",
            hostname="localhost",
            attributes={"attribute": "example"},
        )

        assert user.serialize_attrs() == '{"attribute": "example"}'
