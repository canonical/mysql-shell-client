# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from mysql_shell.builders import StringQueryQuoter


@pytest.mark.unit
class TestStringQueryQuoter:
    """Class to group all the StringQueryQuoter tests."""

    def test_quote_value(self):
        """Test the quote_value method."""
        quoter = StringQueryQuoter()

        assert quoter.quote_value("test") == "'test'"
        assert quoter.quote_value("'; injected code ;'") == "'\\'; injected code ;\\''"

    def test_quote_identifier(self):
        """Test the quote_identifier method."""
        quoter = StringQueryQuoter()

        assert quoter.quote_identifier("test") == "`test`"
        assert quoter.quote_value("`; injected code ;`") == "'\\`; injected code ;\\`'"
