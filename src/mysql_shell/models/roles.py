# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from enum import Enum


class ClusterRole(str, Enum):
    """MySQL cluster roles."""

    PRIMARY = "PRIMARY"
    REPLICA = "REPLICA"


class InstanceRole(str, Enum):
    """MySQL instance roles."""

    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
