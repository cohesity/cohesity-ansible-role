# Cohesity Facts

## SYNOPSIS
The Ansible Module collects and compiles details about a Cohesity cluster.  The data can be compiled and returned as a variable, which can then be used to perform actions based on the collected information.

### Requirements
* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Tip:**  Currently, the Ansible Module requires Full Cluster Administrator access.

## SYNTAX

```yaml
- cohesity_facts:
    server: <ip or hostname for cohesity cluster>
    cohesity_admin: <username with cluster level permissions>
    cohesity_password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <level of data collection>
    include_sources: <boolean to determine if specific information should be collected>
    include_jobs: <boolean to determine if specific information should be collected>
    include_runs: <boolean to determine if specific information should be collected>
    active_only: <boolean to determine if only active jobs should be collected>
    include_deleted: <boolean to determine if results should include deleted items>
```

## EXAMPLES

```yaml
# Gather facts about all nodes and supported resources in a cluster
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password

# Gather facts about all nodes and protection sources in a cluster
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password
    state: minimal
    include_sources: True

# Gather facts about all nodes and return active job executions in a cluster
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password
    state: minimal
    include_runs: True
    active_only: True

```


## PARAMETERS

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster. Domain-specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**complete**<br>-minimal | Determines what the level of collection should be *complete* or *absent* from the cluster.  If *complete*, then all data is collected automatically regardless of the specified inclusions excluding `include_deleted`. |
|   | include_sources | Boolean | False | Determines whether the specified resource information is collected. |
|   | include_jobs | Boolean | False | Determines whether the specified resource information is collected. |
|   | include_runs | Boolean | False | Determines whether the specified resource information is collected. |
|   | active_only | Boolean | False | Determines whether only active jobs are collected. |
|   | include_deleted | Boolean | False | Determines whether results include deleted items. |

## OUTPUTS
- N/A

