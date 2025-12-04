# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
from typing import Any

from ..builders import StringQueryQuoter
from ..executors import BaseExecutor
from ..executors.errors import ExecutionError
from ..models.account import Role, User
from ..models.roles import InstanceRole
from ..models.statement import LogType, VariableScope
from ..models.status import InstanceStatus

logger = logging.getLogger()

Attributes = dict[str, str] | None


class MySQLInstanceClient:
    """Class to encapsulate all instance operations using MySQL Shell."""

    def __init__(self, executor: BaseExecutor, quoter: StringQueryQuoter):
        """Initialize the class."""
        self._executor = executor
        self._quoter = quoter

    def check_work_ongoing(self, name_pattern: str) -> bool:
        """Checks whether an instance work is ongoing."""
        query = (
            "SELECT work_completed, work_estimated "
            "FROM performance_schema.events_stages_current "
            "WHERE event_name LIKE {name_pattern}"
        )
        query = query.format(
            name_pattern=self._quoter.quote_value(name_pattern),
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to check work for events with {name_pattern=}")
            raise
        else:
            return any(row["work_completed"] < row["work_estimated"] for row in rows)

    def create_instance_role(self, role: Role, roles: list[str] = None) -> None:
        """Creates a new instance role."""
        if not roles:
            granting_query = ""
        else:
            granting_query = "GRANT {roles} TO {rolename}@{hostname}"
            granting_query = granting_query.format(
                rolename=self._quoter.quote_value(role.rolename),
                hostname=self._quoter.quote_value(role.hostname),
                roles=", ".join(self._quoter.quote_value(r) for r in roles),
            )

        creation_query = "CREATE ROLE {rolename}@{hostname}"
        creation_query = creation_query.format(
            rolename=self._quoter.quote_value(role.rolename),
            hostname=self._quoter.quote_value(role.hostname),
        )

        queries = ";".join((
            creation_query,
            granting_query,
        ))

        try:
            self._executor.execute_sql(queries)
        except ExecutionError:
            logger.error(f"Failed to create instance role {role.rolename}.{role.hostname}")
            raise

    def create_instance_user(self, user: User, password: str, roles: list[str] = None) -> None:
        """Creates an instance user with the provided attributes."""
        if not roles:
            granting_query = ""
        else:
            granting_query = "GRANT {roles} TO {username}@{hostname}"
            granting_query = granting_query.format(
                username=self._quoter.quote_value(user.username),
                hostname=self._quoter.quote_value(user.hostname),
                roles=", ".join(self._quoter.quote_value(r) for r in roles),
            )

        creation_query = (
            "CREATE USER {username}@{hostname} IDENTIFIED BY {password} ATTRIBUTE {attrs}"
        )
        creation_query = creation_query.format(
            username=self._quoter.quote_value(user.username),
            hostname=self._quoter.quote_value(user.hostname),
            password=self._quoter.quote_value(password),
            attrs=self._quoter.quote_value(user.serialize_attrs()),
        )

        queries = ";".join((
            creation_query,
            granting_query,
        ))

        try:
            self._executor.execute_sql(queries)
        except ExecutionError:
            logger.error(f"Failed to create instance user {user.username}.{user.hostname}")
            raise

    def delete_instance_user(self, user: User) -> None:
        """Deletes an instance user if it exists."""
        query = "DROP USER IF EXISTS {username}@{hostname}"
        query = query.format(
            username=self._quoter.quote_value(user.username),
            hostname=self._quoter.quote_value(user.hostname),
        )

        try:
            self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to delete instance user {user.username}.{user.hostname}")
            raise

    def delete_instance_users(self, users: list[User]) -> None:
        """Deletes the instance users provided."""
        query = "DROP USER IF EXISTS {username}@{hostname}"
        queries = []

        for user in users:
            queries.append(
                query.format(
                    username=self._quoter.quote_value(user.username),
                    hostname=self._quoter.quote_value(user.hostname),
                )
            )

        queries = ";".join(queries)

        try:
            self._executor.execute_sql(queries)
        except ExecutionError:
            logger.error("Failed to delete instance users")
            raise

    def update_instance_user(self, user: User, password: str) -> None:
        """Updates an instance user with the provided password."""
        query = "ALTER USER {username}@{hostname} IDENTIFIED BY {password}"
        query = query.format(
            username=self._quoter.quote_value(user.username),
            hostname=self._quoter.quote_value(user.hostname),
            password=self._quoter.quote_value(password),
        )

        try:
            self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to update instance user {user.username}.{user.hostname}")
            raise

    def flush_instance_logs(self, logs: list[LogType]) -> None:
        """Flushes the instance logs."""
        if not logs:
            return

        bin_logging = self.get_instance_variable(VariableScope.SESSION, "sql_log_bin")

        try:
            self.set_instance_variable(VariableScope.SESSION, "sql_log_bin", "OFF")

            query = "FLUSH {log} LOGS"
            queries = [query.format(log=log.value) for log in logs]
            queries = ";".join(queries)

            self._executor.execute_sql(queries)
        except ExecutionError:
            logger.error("Failed to flush instance logs")
            raise
        finally:
            self.set_instance_variable(VariableScope.SESSION, "sql_log_bin", bin_logging)

    def get_cluster_instance_label(self) -> str:
        """Gets the instance label within the cluster."""
        query = (
            "SELECT instance_name "
            "FROM mysql_innodb_cluster_metadata.instances "
            "WHERE mysql_server_uuid = @@server_uuid"
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error("Failed to get cluster instance label")
            raise
        else:
            return rows[0]["instance_name"]

    def get_cluster_instance_labels(self, cluster_name: str) -> list[str]:
        """Gets the instance labels within the cluster."""
        query = (
            "SELECT instance_name "
            "FROM mysql_innodb_cluster_metadata.instances "
            "WHERE cluster_name = {cluster_name}"
        )
        query = query.format(
            cluster_name=self._quoter.quote_value(cluster_name),
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to get cluster instance labels with {cluster_name=}")
            raise
        else:
            return [row["instance_name"] for row in rows]

    def get_instance_replication_state(self) -> InstanceStatus:
        """Gets the instance replication state."""
        query = (
            "SELECT member_state "
            "FROM performance_schema.replication_group_members "
            "WHERE member_id = @@server_uuid"
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error("Failed to get instance replication state")
            raise
        else:
            return InstanceStatus(rows[0]["member_state"])

    def get_instance_replication_role(self) -> InstanceRole:
        """Gets the instance replication role."""
        query = (
            "SELECT member_role "
            "FROM performance_schema.replication_group_members "
            "WHERE member_id = @@server_uuid"
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error("Failed to get instance replication role")
            raise
        else:
            return InstanceRole(rows[0]["member_role"])

    def get_instance_variable(self, scope: VariableScope, name: str) -> Any:
        """Gets an instance variable by scope and name."""
        escaped_name = self._quoter.escape(name)

        query = "SELECT @@{scope}.{name} AS {alias}"
        query = query.format(
            scope=scope.value,
            name=escaped_name,
            alias=escaped_name,
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to get instance variable {scope}.{name}")
            raise
        else:
            return rows[0][name]

    def set_instance_variable(self, scope: VariableScope, name: str, value: Any) -> None:
        """Sets an instance variable by scope and name."""
        escaped_name = self._quoter.escape(name)
        escaped_value = self._quoter.escape(value)

        if escaped_value != value:
            raise ValueError(f"Invalid value for instance variable {scope}.{name}")

        query = "SET @@{scope}.{name} = {value}"
        query = query.format(
            scope=scope.value,
            name=escaped_name,
            value=escaped_value,
        )

        try:
            self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to set instance variable {scope}.{name}")
            raise

    def get_instance_version(self) -> str:
        """Gets the instance version value."""
        return self.get_instance_variable(VariableScope.GLOBAL, "version").split("-")[0]

    def get_instance_read_only(self) -> bool:
        """Gets the instance read-only value."""
        return self.get_instance_variable(VariableScope.GLOBAL, "super_read_only") == 1

    def install_instance_plugin(self, name: str, path: str) -> None:
        """Installs an instance plugin by name and path."""
        query = "INSTALL PLUGIN {plugin_name} SONAME {plugin_path}"
        query = query.format(
            plugin_name=self._quoter.quote_identifier(name),
            plugin_path=self._quoter.quote_value(path),
        )

        try:
            self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to install instance plugin with {name=} and {path=}")
            raise

    def uninstall_instance_plugin(self, name: str) -> None:
        """Uninstalls an instance plugin by name."""
        query = "UNINSTALL PLUGIN {plugin_name}"
        query = query.format(
            plugin_name=self._quoter.quote_identifier(name),
        )

        try:
            self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to uninstall instance plugin with {name=}")
            raise

    def search_instance_databases(self, name_pattern: str) -> list[str]:
        """Searches the instance databases by name pattern."""
        query = (
            "SELECT schema_name "
            "FROM information_schema.schemata "
            "WHERE schema_name LIKE {name_pattern}"
        )
        query = query.format(
            name_pattern=self._quoter.quote_value(name_pattern),
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to search instance databases with {name_pattern=}")
            raise
        else:
            return [row["SCHEMA_NAME"] for row in rows]

    def search_instance_plugins(self, name_pattern: str) -> list[str]:
        """Searches the instance plugins by name pattern."""
        # fmt: off
        query = (
            "SELECT name "
            "FROM mysql.plugin "
            "WHERE name LIKE {name_pattern}"
        )
        # fmt: on

        query = query.format(
            name_pattern=self._quoter.quote_value(name_pattern),
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to search instance plugins with {name_pattern=}")
            raise
        else:
            return [row["name"] for row in rows]

    def search_instance_roles(self, name_pattern: str) -> list[Role]:
        """Searches the instance roles by name pattern."""
        query = (
            "SELECT user, host "
            "FROM mysql.user "
            "WHERE user LIKE {name_pattern} AND authentication_string=''"
        )
        query = query.format(
            name_pattern=self._quoter.quote_value(name_pattern),
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to search instance roles with {name_pattern=}")
            raise
        else:
            return [Role.from_row(row["user"], row["host"]) for row in rows]

    def search_instance_users(self, name_pattern: str, attrs: Attributes = None) -> list[User]:
        """Searches the instance users by name pattern and attributes."""
        attr_filter = "attribute LIKE {string}"
        attr_substr = '%"{key}": "{val}"%'

        if not attrs:
            strings = ["%"]
            filters = [attr_filter.format(string=self._quoter.quote_value(s)) for s in strings]
        else:
            strings = [attr_substr.format(key=key, val=val) for key, val in attrs.items()]
            filters = [attr_filter.format(string=self._quoter.quote_value(s)) for s in strings]

        query = (
            "SELECT user, host, attribute "
            "FROM information_schema.user_attributes "
            "WHERE user LIKE {name_pattern} AND {attr_filters}"
        )
        query = query.format(
            name_pattern=self._quoter.quote_value(name_pattern),
            attr_filters=" AND ".join(filters),
        )

        try:
            rows = self._executor.execute_sql(query)
        except ExecutionError:
            logger.error(f"Failed to search instance users with {name_pattern=}")
            raise
        else:
            return [User.from_row(row["USER"], row["HOST"], row["ATTRIBUTE"]) for row in rows]

    def start_instance_replication(self) -> None:
        """Starts instance group replication."""
        query = "START GROUP_REPLICATION"

        try:
            self._executor.execute_sql(query)
        except ExecutionError:
            logger.error("Failed to start instance replication")
            raise

    def stop_instance_replication(self) -> None:
        """Stops instance group replication."""
        query = "STOP GROUP_REPLICATION"

        try:
            self._executor.execute_sql(query)
        except ExecutionError:
            logger.error("Failed to stop instance replication")
            raise
