# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from enum import Enum


class ClusterSetStatus(str, Enum):
    """MySQL cluster-set statuses.

    https://dev.mysql.com/doc/mysql-shell/8.0/en/innodb-clusterset-status.html
    """

    HEALTHY = "HEALTHY"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class ClusterStatus(str, Enum):
    """MySQL cluster statuses.

    There is a slight discrepancy between the possible cluster statuses reported
    on different MySQL documentation pages, this list contains the common ones across them.
    - https://dev.mysql.com/doc/mysql-shell/8.0/en/innodb-clusterset-status.html
    - https://dev.mysql.com/doc/mysql-shell/8.0/en/monitoring-innodb-cluster.html
    """

    OK = "OK"
    OK_PARTIAL = "OK_PARTIAL"
    OK_NO_TOLERANCE = "OK_NO_TOLERANCE"
    OK_NO_TOLERANCE_PARTIAL = "OK_NO_TOLERANCE_PARTIAL"
    NO_QUORUM = "NO_QUORUM"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    UNREACHABLE = "UNREACHABLE"
    UNKNOWN = "UNKNOWN"


class InstanceStatus(str, Enum):
    """MySQL instance statuses.

    There is a slight discrepancy between the possible instance statuses reported
    by different MySQL mechanisms, this list contains the common ones across them.
    - https://dev.mysql.com/doc/refman/8.0/en/group-replication-server-states.html
    - https://dev.mysql.com/doc/mysql-shell/8.0/en/monitoring-innodb-cluster.html
    """

    ONLINE = "ONLINE"
    RECOVERING = "RECOVERING"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    UNREACHABLE = "UNREACHABLE"
    UNKNOWN = "UNKNOWN"


class InstanceRole(str, Enum):
    """MySQL instance roles."""

    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
