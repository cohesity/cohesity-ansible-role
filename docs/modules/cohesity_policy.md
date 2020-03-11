# Cohesity Policy Management - Linux

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - Policy Management
    - [Create a Protection Policy](#Create-a-Protection-Policy)
    - [Modify a Protection Policy](#Modify-a-Protection-Policy)
    - [Delete a Protection Policy](#Delete-a-Protection-Policy)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-policy-management---linux)

The Ansible Module creates, modifies or deletes a Protection Policy for the Cohesity Cluster

### Requirements
[top](#cohesity-policy-management---linux)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - When using the default download location, the Cohesity agent installer is placed in `/tmp/<temp-dir`.  If your environment prevents the use of `/tmp` with a `noexec` option, then you must set an alternate location.

## Syntax
[top](#cohesity-policy-management---linux)

```yaml
- cohesity_policy:
    cluster: <ip or hostname for cohesity cluster>
    username: <cohesity username with cluster level permissions>
    password: <cohesity password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    name: <Name of the Protection Policy>
    description: <Protection Policy Description>
    state: <Determines if the Protection Policy should be present or absent from the host>
    days_to_retain: <Retains backup or 'days_to_retain' number of days>
    incremental_backup_schedule: <Specify the incremental backup schedule in Protection Policy>
    full_backup_schedule: <ASK_TEAM>
    blackout_window: <Specify the blackout window for retries>
    retries: <Specify the retry value for retries>
    retry_interval: <Specify the retry_interval value for retries>
    bmr_backup_schedule: <Specify the BMR backup schedule for the Protection Policy>
    log_backup_schedule: <Specify the Log Backup for the Protection Policy>
    extended_retention: <Specify the Extended schedule for the Protection Policy>
    archival_copy: <Specify the Archival details for the Protection Policy>
```

## Examples
[top](#cohesity-policy-management---linux)

### Create a Protection Policy
[top](#cohesity-policy-management---linux)

```yaml
- cohesity_policy:
    name: POLICY_NAME
    incremental_backup_schedule: ASK_TEAM
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
```

### Modify a Protection Policy
[top](#cohesity-policy-management---linux)

```yaml
- cohesity_policy:
    name: POLICY_NAME
    incremental_backup_schedule: ASK_TEAM
    cluster: cohesity.lab
    username: admin
    password: password
    state: absent
```

### Delete a Protection Policy
[top](#cohesity-policy-management---linux)

```yaml
- cohesity_policy:
    name: POLICY_NAME
    incremental_backup_schedule: ASK_TEAM
    cluster: cohesity.lab
    username: admin
    password: password
    state: absent
```

## Parameters
[top](#cohesity-policy-management---linux)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **name** | String | | Name of the Protection Policy. |
|  | description | String | | Protection Policy Description.|
|  | state | Choice | -**present**<br>-absent | Determines if the Protection Policy should be present or absent from the host.|
|  | days_to_retain | Integer | 30 | Retains backup or 'days_to_retain' number of days.|
| X | **incremental_backup_schedule** | String | | Specify the incremental backup schedule in Protection Policy.|
|   | full_backup_schedule | dict | False | ASK_TEAM |
|   | blackout_window | dict | False | Specify the blackout window for retries. |
|   | retries | Choice | -**present**<br>-absent | Determines whether the agent is *present* or *absent* from the host. |
|   | retry_interval | Integer | | Specify the retry_interval value for retries.|
|   | bmr_backup_schedule | Dict | | Specify the BMR backup schedule for the Protection Policy.|
|   | log_backup_schedule | Dict | | Specify the Log Backup for the Protection Policy.|
|   | extended_retention | List | | Specify the Extended schedule for the Protection Policy.|
|   | archival_copy | List | | Specify the Archival details for the Protection Policy.|


## Outputs
[top](#cohesity-policy-management---linux)
- N/A

