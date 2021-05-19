# Cohesity Oracle Protection Job

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Create a new Oracle Server Protection Job](#Create-a-new-Oracle-Server-Protection-Job)
  - [Remove an existing Oracle Server Protection Job](#Remove-an-existing-Oracle-Server-Protection-Job)
  - [Start an existing Oracle Server Protection Job](#Start-an-existing-Oracle-Server-Protection-Job)
  - [Stop an actively running Oracle Server Protection Job](#Stop-an-actively-running-Oracle-Server-Protection-Job)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-oracle-protection-job)

This Ansible Module is used to register, remove, start, and stop the Cohesity Protection Job on a Cohesity cluster.  When executed in a playbook, the Cohesity Protection Job is validated and the appropriate state action is applied.

### Requirements
[top](#cohesity-oracle-protection-job)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-oracle-protection-job)

```yaml
- cohesity_oracle_job:
    cluster: <ip or hostname for cohesity cluster>
    username: <username with cluster level permissions>
    password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Protection Job>
    name: <assigned name of the Protection Job>
    endpoint: <Ip or fqdn of  registered Oracle protection sources>
    protection_policy: <existing protection policy name to assign to the job>
    storage_domain: <existing storage domain name to assign to the job>
    time_zone: <time_zone for the protection job>
    delete_backups: <boolean to determine if backups be deleted when job removed>
    cancel_active: <boolean to determine if an active job should be canceled>
```

## Examples
[top](#cohesity-oracle-protection-job)

### Create a new Oracle Server Protection Job
[top](#cohesity-oracle-protection-job)

```yaml
- cohesity_oracle_job:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: myhost
    endpoint: orcl-serv2-eng-db.com
    protection_policy: Bronze
    storage_domain: Default
```

### Remove an existing Oracle Server Protection Job
[top](#cohesity-oracle-protection-job)

```yaml
- cohesity_oracle_job:
    cluster: cohesity.lab
    username: admin
    password: password
    state: absent
    name: myoracle

```

### Start an existing Oracle Server Protection Job
[top](#cohesity-oracle-protection-job)

```yaml
- cohesity_oracle_job:
    cluster: cohesity.lab
    username: admin
    password: password
    state: started
    name: myoracle

```

### Stop an actively running Oracle Server Protection Job
[top](#cohesity-oracle-protection-job)

```yaml
- cohesity_oracle_job:
    cluster: cohesity.lab
    username: admin
    password: password
    state: stopped
    name: myoracle

```

## Parameters
[top](#cohesity-oracle-protection-job)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as <br>- username@domain or domain/username (will be deprecated in future).|
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent<br>-started<br>-stopped | Determines the state of the Protection Job. |
| X | name | String | | Name to assign to the Protection Job.  Must be unique. |
|   | protection_policy | String |  | Valid policy name or ID for an existing Protection Policy to be assigned to the job. **Required** when *state=present*. |
|   | storage_domain | String | | Existing Storage Domain with which the Protection Job will be associated. Required when *state=present*. |
|   | time_zone | String | America/Los_Angeles | Specifies the time zone to use when calculating time for this Protection Job (such as the Job start time). The time must be specified in the **Area/Location** format, such as "America/New_York". |
|   | delete_backups | Boolean | False | Specifies whether Snapshots generated by the Protection Job should also be deleted when the Job is deleted. Optional and valid only when *state=absent*. |
|   | cancel_active | Boolean | False | Specifies whether the Current Running Backup Job is canceled.  If *False*, active jobs are not stopped and a failure is raised. Optional and valid only when *state=stopped* |
|   | endpoint | String | | Specifies the source ip or hostname **Required** when *state=present*. |
## Outputs
[top](#cohesity-oracle-protection-job)

- Returns the registered Protection Job ID

