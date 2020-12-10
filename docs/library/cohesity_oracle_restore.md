# Cohesity Restore

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Restore a single database from a Oracle Backup](#Restore-a-single-database-from-a-Oracle-Source-to-another-Source)
  - [Restore database to a view](#Restore-database-to-a-view)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-restore)

This Ansible Module supports database restore operation for the chosen Cohesity Protection Job on a Cohesity cluster to same source or a different oracle source.  When executed in a playbook, the Cohesity restore operation is validated and the appropriate restore action is applied.

### Requirements
[top](#cohesity-restore)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-restore)

```yaml
- cohesity_oracle_restore:
    cluster: <ip or hostname for cohesity cluster>
    username: <cohesity username with cluster level permissions>
    password: <cohesity password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the restore operation>
    task_name: <name of the restore job>
    view_name: <Name of view to write database files>
    source_server: <Name of the source server>
    source_db: <Name of the database available in source server which needs to be restored>
    targe_server: <Name of the target server>
    target_db: <database is restores under the provided name in target server>
    oracle_home: <path to oracle home directory>
    oracle_base: <path to oracle base directory>
    oracle_data: <path to oracle data directory>
```

## Examples
[top](#cohesity-restore)

### Restore a single database from a Oracle Source to another Source
[top](#cohesity-restore)

```yaml
- cohesity_oracle_restore:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    task_name: Restore task name
    source_server: orcl-serv2-eng-db.com
    source_db: database_1
    target_server: orcl-serv1-eng-db.com
    target_db: database_2
    oracle_home: /path/to/oracle/home
    oracle_base: /path/to/oracle/base
    oracle_data: /path/to/oracle/home

```

### Restore database to a view
[top](#cohesity-restore)

```yaml
- cohesity_oracle_restore:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    task_name: Restore task name
    source_server: orcl-serv2-eng-db.com
    source_db: database_1
    view_name: myview

```

## Parameters
[top](#cohesity-restore)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as.<br>- username@domain or domain/username (will be deprecated in future).|
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
| X | **task_name** | String | | Name of the Restore Job.  |
|   | view_name | String | | Name of the view, where database files are restored. Required if the file is restored to view.  |
| X | **source_server** | String | | Name of the Source server where database is present.  |
| X | **source_db** | String | | Name of the database to restore.  |
|   | target_server | String | | Name of the target server. Required if the files are restored to a server.  |
|   | target_db | String | | Name of the database which will be created in target server. Required if the files are restored to a server  |
|   | oracle_home | String | | Path to oracle home directory. Required if the files are restored to a server  |
|   | oracle_base | String | | Path to oracle base directory. Required if the files are restored to a server  |
|   | oracle_data | String | | Path to oracle data directory. Required if the files are restored to a server  |


## Outputs
[top](#cohesity-restore)

- Returns the restore operation details as an array of Restore Job details.