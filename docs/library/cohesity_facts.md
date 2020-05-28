# Cohesity Facts

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Gather facts about all nodes and supported resources in a cluster](#Gather-facts-about-all-nodes-and-supported-resources-in-a-cluster)
  - [Gather facts about all nodes and protection sources in a cluster](#Gather-facts-about-all-nodes-and-protection-sources-in-a-cluster)
  - [Gather facts about all nodes and return active job executions in a cluster](#Gather-facts-about-all-nodes-and-return-active-job-executions-in-a-cluster)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-facts)

This Ansible Module collects and compiles details about a Cohesity cluster.  The data can be compiled and returned as a variable, which can then be used to perform actions based on the collected information.

```json
{
  "cluster": {
    "nodes": [
          Array of Cohesity Node Details
    ],
    "protection": {
      "jobs": [
         Array of Job Details
      ],
      "policies": [
         Array of Backup Policy Information
      ],
      "runs": [
         Array of Backup executions
      ],
      "sources": {
        "GenericNas": [
           Array of GenericNas Protection Sources
        ],
        "Physical": [
           Array of Physical Protection Sources
        ],
        "VMware":  [
           Array of VMware Protection Sources
        ],
      }
    },
    "storage_domains": [
           Array of Cohesity Backup Storage Domains
    ],
  }
}
```

### Requirements
[top](#cohesity-facts)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-facts)


```yaml
- cohesity_facts:
    cluster: <ip or hostname for cohesity cluster>
    username: <username with cluster level permissions>
    password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <level of data collection>
    include_sources: <boolean to determine if specific information should be collected>
    include_jobs: <boolean to determine if specific information should be collected>
    include_runs: <boolean to determine if specific information should be collected>
    active_only: <boolean to determine if only active jobs should be collected>
    include_deleted: <boolean to determine if results should include deleted items>
```

## Examples
[top](#cohesity-facts)

### Gather facts about all nodes and supported resources in a cluster
[top](#cohesity-facts)

```yaml
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password
```
### Gather facts about all nodes and protection sources in a cluster
[top](#cohesity-facts)

```yaml
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password
    state: minimal
    include_sources: True
```

### Gather facts about all nodes and return active job executions in a cluster
[top](#cohesity-facts)

```yaml
- cohesity_facts:
    cluster: cohesity.lab
    username: admin
    password: password
    state: minimal
    include_runs: True
    active_only: True

```


## Parameters
[top](#cohesity-facts)


| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as <br>- username@domain or Domain/username (will be deprecated in future). |
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**complete**<br>-minimal | Determines the level of data collection from the cluster: *complete* or *minimal*.<br>- If *complete*, all data is collected automatically regardless of any *include_X* settings, with the exception of the `include_deleted` option; if `include_deleted` is set to **False**, jobs and sources that are marked as _deleted_ are ignored.<br>- If *minimal*, only the base information about the cluster and nodes is collected. If additional *include_X* items are set to **True**, those items are also included. |
|   | include_sources | Boolean | False | Determines whether the specified resource information is collected. |
|   | include_jobs | Boolean | False | Determines whether the specified resource information is collected. |
|   | include_runs | Boolean | False | Determines whether the specified resource information is collected. |
|   | active_only | Boolean | False | Determines whether only active jobs are collected. |
|   | include_deleted | Boolean | False | Determines whether results include deleted items. |

## Outputs
[top](#cohesity-facts)

```json
{
  "cluster": {
    "nodes": [
           Array of Cohesity Node Details
    ],
    "protection": {
      "jobs": [
         Array of Job Details
      ],
      "policies": [
         Array of Backup Policy Information
      ],
      "runs": [
         Array of Backup executions
      ],
      "sources": {
        "GenericNas": [
           Array of GenericNas Protection Sources
        ],
        "Physical": [
           Array of Physical Protection Sources
        ],
        "VMware":  [
           Array of VMware Protection Sources
        ],
      }
    },
    "storage_domains": [
           Array of Cohesity Backup Storage Domains
    ],
  }
}
```
