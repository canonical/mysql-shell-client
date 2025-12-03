# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog][docs-changelog], and the version adheres to [Semantic Versioning][docs-semver].


## Unreleased
### Added
- Timeout to cluster / cluster-set status fetching.
### Fixed
- Invalid InstanceStatus enum value.

## [0.2.0][changes-0.2.0] - 2025-12-03
### Added
- Lock fetching method to LockQueryBuilder classes.
- Instance-promote method to ClusterClient class.
- Instance-rejoin method to ClusterClient class.
- Instance-check method to ClusterClient class.
- Cluster-set cluster status enum.
- Complete error message to the LocalExecutor raised exception
### Fixed
- Crash when querying instance role and instance status.
- Possible password leak in LocalExecutor traceback info.

## [0.1.0][changes-0.1.0] - 2025-12-01
### Added
- Initial functionality.
- Initial test suite.
- Initial documentation.


[changes-0.1.0]: https://github.com/canonical/mysql-shell-client/releases/tag/0.1.0
[changes-0.2.0]: https://github.com/canonical/mysql-shell-client/compare/0.1.0...0.2.0
[docs-changelog]: https://keepachangelog.com/en/1.0.0/
[docs-semver]: https://semver.org/spec/v2.0.0.html
