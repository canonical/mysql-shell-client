# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import logging
from typing import Mapping

from ..executors import BaseExecutor
from ..executors.errors import ExecutionError

logger = logging.getLogger()

_Options = Mapping[str, str] | None


class MySQLClusterClient:
    """Class to encapsulate all cluster operations using MySQL Shell."""

    def __init__(self, executor: BaseExecutor):
        """Initialize the class."""
        self._executor = executor

    def create_cluster(self, cluster_name: str, options: _Options = None) -> None:
        """Creates an InnoDB cluster."""
        command = f"dba.create_cluster('{cluster_name}', {options})"

        try:
            logger.debug(f"Creating InnoDB cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to create cluster {cluster_name}")
            raise

    def destroy_cluster(self, cluster_name: str, options: _Options = None) -> None:
        """Destroys an InnoDB cluster."""
        command = "\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.dissolve({options})",
        ))

        try:
            logger.debug(f"Destroying InnoDB cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to destroy cluster {cluster_name}")
            raise

    def fetch_cluster_status(self, cluster_name: str, extended: bool = False) -> dict:
        """Fetches an InnoDB cluster status."""
        command = "\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"status = cluster.status({{'extended': {extended}}})",
            f"print(status)",
        ))

        try:
            result = self._executor.execute_py(command, timeout=30)
        except ExecutionError:
            logger.error("Failed to fetch cluster status")
            raise
        else:
            return json.loads(result)

    def list_cluster_routers(self, cluster_name: str) -> dict:
        """Lists an InnoDB cluster connected MySQL Routers."""
        command = "\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"routers = cluster.list_routers()",
            f"print(routers)",
        ))

        try:
            result = self._executor.execute_py(command)
        except ExecutionError:
            logger.error("Failed to list cluster routers")
            raise
        else:
            return json.loads(result)

    def rescan_cluster(self, cluster_name: str, options: _Options = None) -> None:
        """Rescans an InnoDB cluster."""
        command = "\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.rescan({options})",
        ))

        try:
            logger.debug(f"Re-scanning InnoDB cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to re-scan cluster {cluster_name}")
            raise

    def reboot_cluster(self, cluster_name: str, options: _Options = None) -> None:
        """Reboots an InnoDB cluster."""
        command = f"dba.reboot_cluster_from_complete_outage('{cluster_name}', {options})"

        try:
            logger.debug(f"Re-booting InnoDB cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to re-boot cluster {cluster_name}")
            raise

    def create_cluster_set(self, cluster_name: str, cluster_set_name: str) -> None:
        """Creates an InnoDB cluster set from the provided cluster."""
        command = "\n".join((
            f"shell.connect_to_primary()",
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.create_cluster_set('{cluster_set_name}')",
        ))

        try:
            logger.debug(f"Creating InnoDB cluster set {cluster_set_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to create cluster set {cluster_set_name}")
            raise

    def fetch_cluster_set_status(self, extended: bool = False) -> dict:
        """Fetches an InnoDB cluster set status."""
        command = "\n".join((
            f"shell.connect_to_primary()",
            f"cluster_set = dba.get_cluster_set()",
            f"status = cluster_set.status({{'extended': {extended}}})",
            f"print(status)",
        ))

        try:
            result = self._executor.execute_py(command, timeout=120)
        except ExecutionError:
            logger.error("Failed to fetch cluster set status")
            raise
        else:
            return json.loads(result)

    def list_cluster_set_routers(self) -> dict:
        """Lists an InnoDB cluster set connected MySQL Routers."""
        command = "\n".join((
            f"shell.connect_to_primary()",
            f"cluster_set = dba.get_cluster_set()",
            f"routers = cluster_set.list_routers()",
            f"print(routers)",
        ))

        try:
            result = self._executor.execute_py(command)
        except ExecutionError:
            logger.error("Failed to list cluster set routers")
            raise
        else:
            return json.loads(result)

    def create_cluster_set_replica(
        self,
        cluster_name: str,
        source_host: str,
        source_port: str,
        options: _Options = None,
    ) -> None:
        """Creates an InnoDB replica cluster into the cluster set."""
        address = f"{source_host}:{source_port}"
        command = f"\n".join((
            f"shell.connect_to_primary()",
            f"cluster_set = dba.get_cluster_set()",
            f"cluster_set.create_replica_cluster('{address}', '{cluster_name}', {options})",
        ))

        try:
            logger.debug(f"Creating InnoDB cluster set replica {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to create cluster set replica {cluster_name}")
            raise

    def promote_cluster_set_replica(self, cluster_name: str, force: bool = False) -> None:
        """Promotes an InnoDB replica cluster within the cluster set."""
        if force:
            logger.warning(f"Forcing cluster {cluster_name} to become primary")
            method_name = "force_primary_cluster"
        else:
            logger.debug(f"Setting cluster {cluster_name} to become primary")
            method_name = "set_primary_cluster"

        command = "\n".join((
            f"shell.connect_to_primary()",
            f"cluster_set = dba.get_cluster_set()",
            f"cluster_set.{method_name}('{cluster_name}')",
        ))

        try:
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to make cluster {cluster_name} the primary")
            raise

    def remove_cluster_set_replica(self, cluster_name: str, options: _Options = None) -> None:
        """Removes an InnoDB replica cluster from the cluster set."""
        command = "\n".join((
            f"shell.connect_to_primary()",
            f"cluster_set = dba.get_cluster_set()",
            f"cluster_set.remove_cluster('{cluster_name}', {options})",
        ))

        try:
            logger.debug(f"Removing InnoDB cluster set replica {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to remove cluster set replica {cluster_name}")
            raise

    def rejoin_cluster_set_cluster(self, cluster_name: str) -> None:
        """Rejoins an InnoDB cluster back to its cluster set."""
        command = "\n".join((
            f"shell.connect_to_primary()",
            f"cluster_set = dba.get_cluster_set()",
            f"cluster_set.rejoin_cluster('{cluster_name}')",
        ))

        try:
            logger.debug(f"Rejoining cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to rejoin cluster {cluster_name}")
            raise

    def attach_instance_into_cluster(
        self,
        cluster_name: str,
        instance_host: str,
        instance_port: str,
        options: _Options = None,
    ) -> None:
        """Attached an instance into an InnoDB cluster."""
        address = f"{instance_host}:{instance_port}"
        command = f"\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.add_instance('{address}', {options})",
        ))

        try:
            logger.debug(f"Attaching instance {address} to cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to attach instance {address} to cluster {cluster_name}")
            raise

    def detach_instance_from_cluster(
        self,
        cluster_name: str,
        instance_host: str,
        instance_port: str,
        options: _Options = None,
    ) -> None:
        """Detaches an instance from an InnoDB cluster."""
        address = f"{instance_host}:{instance_port}"
        command = f"\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.remove_instance('{address}', {options})",
        ))

        try:
            logger.debug(f"Detaching instance {address} from cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to detach instance {address} from cluster {cluster_name}")
            raise

    def force_instance_quorum_into_cluster(
        self,
        cluster_name: str,
        instance_host: str,
        instance_port: str,
    ) -> None:
        """Forces and instance quorum into an InnoDB cluster."""
        address = f"{instance_host}:{instance_port}"
        command = f"\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.force_quorum_using_partition_of('{address}')",
        ))

        try:
            logger.debug(f"Forcing quorum into cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to force quorum into cluster {cluster_name}")
            raise

    def rejoin_instance_into_cluster(
        self,
        cluster_name: str,
        instance_host: str,
        instance_port: str,
        options: _Options = None,
    ) -> None:
        """Rejoins an instance back into its InnoDB cluster."""
        address = f"{instance_host}:{instance_port}"
        command = f"\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.rejoin_instance('{address}', {options})",
        ))

        try:
            logger.debug(f"Rejoining instance {address} into cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to rejoin instance {address} into cluster {cluster_name}")
            raise

    def check_instance_before_cluster(self, options: _Options = None) -> dict:
        """Checks for an instance configuration before joining an InnoDB cluster."""
        command = "\n".join((
            f"result = dba.check_instance_configuration(options={options})",
            f"print(result)",
        ))

        host = self._executor.connection_details.host
        port = self._executor.connection_details.port

        try:
            logger.debug(f"Checking for instance {host}:{port} config")
            result = self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to check for instance {host}:{port} config")
            raise
        else:
            return json.loads(result)

    def setup_instance_before_cluster(self, options: _Options = None) -> None:
        """Sets up an instance configuration before joining an InnoDB cluster."""
        command = f"dba.configure_instance(options={options})"
        host = self._executor.connection_details.host
        port = self._executor.connection_details.port

        try:
            logger.debug(f"Setting up instance {host}:{port} config")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to setup instance {host}:{port} config")
            raise

    def promote_instance_within_cluster(
        self,
        cluster_name: str,
        instance_host: str,
        instance_port: str,
        force: bool = False,
    ) -> None:
        """Promotes an InnoDB cluster replica within the cluster."""
        address = f"{instance_host}:{instance_port}"

        if force:
            logger.warning(f"Forcing instance {address} to become primary")
            method_name = "force_primary_instance"
        else:
            logger.debug(f"Setting instance {address} to become primary")
            method_name = "set_primary_instance"

        command = "\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.{method_name}('{address}')",
        ))

        try:
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to make instance {address} the primary")
            raise

    def update_instance_within_cluster(
        self,
        cluster_name: str,
        instance_host: str,
        instance_port: str,
        options: _Options = None,
    ) -> None:
        """Updates an instance within an InnoDB cluster."""
        address = f"{instance_host}:{instance_port}"
        command = [
            f"cluster = dba.get_cluster('{cluster_name}')",
        ]

        for key, val in options.items():
            val = f"'{val}'" if isinstance(val, str) else val
            cmd = f"cluster.set_instance_option('{address}', '{key}', {val})"
            command.append(cmd)

        command = "\n".join(command)

        try:
            logger.debug(f"Updating instance {address} within cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to update instance {address} within cluster {cluster_name}")
            raise

    def remove_router_from_cluster(
        self,
        cluster_name: str,
        router_name: str,
        router_mode: str,
    ) -> None:
        """Removes a router from an InnoDB cluster."""
        command = "\n".join((
            f"cluster = dba.get_cluster('{cluster_name}')",
            f"cluster.remove_router_metadata('{router_name}::{router_mode}')",
        ))

        try:
            logger.debug(f"Removing router from cluster {cluster_name}")
            self._executor.execute_py(command)
        except ExecutionError:
            logger.error(f"Failed to remove router from cluster {cluster_name}")
            raise
