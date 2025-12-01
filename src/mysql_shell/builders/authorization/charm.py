# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from ..quoting import StringQueryQuoter
from .base import BaseAuthorizationQueryBuilder


class CharmAuthorizationQueryBuilder(BaseAuthorizationQueryBuilder):
    """Charm authorization query builder."""

    ROLE_CREATION_QUERY = "CREATE ROLE {rolename}"
    ROLE_GRANTING_QUERY = "GRANT {parents} TO {rolename}"
    PRIV_GRANTING_QUERY = "GRANT {privileges} ON {database}.* TO {rolename}"

    _DATA_PRIVILEGES = [
        "SELECT",
        "INSERT",
        "DELETE",
        "UPDATE",
        "EXECUTE",
    ]

    _SCHEMA_PRIVILEGES = [
        "ALTER",
        "ALTER ROUTINE",
        "CREATE",
        "CREATE ROUTINE",
        "CREATE VIEW",
        "DROP",
        "INDEX",
        "LOCK TABLES",
        "REFERENCES",
        "TRIGGER",
    ]

    def __init__(
        self,
        role_admin: str,
        role_backup: str,
        role_ddl: str,
        role_stats: str,
        role_reader: str,
        role_writer: str,
    ):
        """Initialize the query builder."""
        self._quoter = StringQueryQuoter()
        self._role_admin = self._quoter.quote_value(role_admin)
        self._role_backup = self._quoter.quote_value(role_backup)
        self._role_ddl = self._quoter.quote_value(role_ddl)
        self._role_stats = self._quoter.quote_value(role_stats)
        self._role_reader = self._quoter.quote_value(role_reader)
        self._role_writer = self._quoter.quote_value(role_writer)

    def _build_instance_admin_role_queries(self) -> list[str]:
        """Builds the instance admin role creation queries."""
        return [
            self.ROLE_CREATION_QUERY.format(
                rolename=self._role_admin,
            ),
            self.ROLE_GRANTING_QUERY.format(
                parents=", ".join([
                    self._role_backup,
                    self._role_ddl,
                    self._role_stats,
                    self._role_writer,
                ]),
                rolename=self._role_admin,
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join([
                    *self._DATA_PRIVILEGES,
                    "EVENT",
                    "SHUTDOWN",
                    "AUDIT_ADMIN",
                    "CONNECTION_ADMIN",
                    "SYSTEM_VARIABLES_ADMIN",
                ]),
                rolename=self._role_admin,
                database="*",
            ),
        ]

    def _build_instance_backup_role_queries(self) -> list[str]:
        """Builds the instance backups role creation queries."""
        return [
            self.ROLE_CREATION_QUERY.format(
                rolename=self._role_backup,
            ),
            self.ROLE_GRANTING_QUERY.format(
                parents=", ".join([self._role_stats]),
                rolename=self._role_backup,
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join([
                    "EXECUTE",
                    "LOCK TABLES",
                    "PROCESS",
                    "RELOAD",
                    "BACKUP_ADMIN",
                    "CONNECTION_ADMIN",
                ]),
                rolename=self._role_backup,
                database="*",
            ),
        ]

    def _build_instance_ddl_role_queries(self) -> list[str]:
        """Builds the instance backups role creation queries."""
        return [
            self.ROLE_CREATION_QUERY.format(
                rolename=self._role_ddl,
            ),
            self.ROLE_GRANTING_QUERY.format(
                parents=", ".join([self._role_writer]),
                rolename=self._role_ddl,
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join([*self._SCHEMA_PRIVILEGES, "SHOW_ROUTINE", "SHOW VIEW"]),
                rolename=self._role_ddl,
                database="*",
            ),
        ]

    def _build_instance_stats_role_queries(self) -> list[str]:
        """Builds the instance stats role creation queries."""
        return [
            self.ROLE_CREATION_QUERY.format(
                rolename=self._role_stats,
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join(["SELECT"]),
                rolename=self._role_stats,
                database="performance_schema",
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join(["PROCESS", "RELOAD", "REPLICATION CLIENT"]),
                rolename=self._role_stats,
                database="*",
            ),
        ]

    def _build_instance_reader_role_queries(self) -> list[str]:
        """Builds the instance reader role creation queries."""
        return [
            self.ROLE_CREATION_QUERY.format(
                rolename=self._role_reader,
            ),
        ]

    def _build_instance_writer_role_queries(self) -> list[str]:
        """Builds the instance writer role creation queries."""
        return [
            self.ROLE_CREATION_QUERY.format(
                rolename=self._role_writer,
            ),
        ]

    def build_instance_auth_roles_query(self) -> str:
        """Builds the instance roles creation query."""
        return ";".join([
            *self._build_instance_reader_role_queries(),
            *self._build_instance_writer_role_queries(),
            *self._build_instance_stats_role_queries(),
            *self._build_instance_ddl_role_queries(),
            *self._build_instance_backup_role_queries(),
            *self._build_instance_admin_role_queries(),
        ])

    def build_instance_router_role_query(self, rolename: str) -> str:
        """Builds the instance router role creation query."""
        rolename = self._quoter.quote_value(rolename)

        return ";".join([
            self.ROLE_CREATION_QUERY.format(
                rolename=rolename,
            ),
            (self.PRIV_GRANTING_QUERY + " WITH GRANT OPTION").format(
                privileges=", ".join(["CREATE USER"]),
                rolename=rolename,
                database="*",
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join([*self._DATA_PRIVILEGES]),
                rolename=rolename,
                database="mysql_innodb_cluster_metadata",
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join(["SELECT"]),
                rolename=rolename,
                database="mysql",
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join(["SELECT"]),
                rolename=rolename,
                database="performance_schema",
            ),
        ])

    def build_database_admin_role_query(self, rolename: str, database: str) -> str:
        """Builds the database admin role creation query."""
        database = self._quoter.quote_identifier(database)
        rolename = self._quoter.quote_value(rolename)

        return ";".join([
            self.ROLE_CREATION_QUERY.format(
                rolename=rolename,
            ),
            self.PRIV_GRANTING_QUERY.format(
                privileges=", ".join([*self._DATA_PRIVILEGES, *self._SCHEMA_PRIVILEGES]),
                rolename=rolename,
                database=database,
            ),
        ])
