# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from enum import Enum


class InstanceRole(str, Enum):
    """MySQL instance roles."""

    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"


class InstanceState(str, Enum):
    """MySQL instance states.

    There is a slight discrepancy between the possible instance states reported
    by different MySQL mechanisms, this list contains the common ones across them.
    - https://dev.mysql.com/doc/refman/8.0/en/group-replication-server-states.html
    - https://dev.mysql.com/doc/mysql-shell/8.0/en/monitoring-innodb-cluster.html
    """

    ONLINE = "ONLINE"
    RECOVERING = "RECOVERING"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    UNREACHABLE = "UNREACHABLE"
