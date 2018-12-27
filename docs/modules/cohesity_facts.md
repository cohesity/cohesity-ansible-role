# Cohesity Facts

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

## SYNOPSIS
[top](#cohesity-facts)

The ansible modules `cohesity_facts` is used to collect and compile details about a Cohesity Cluster.  The data can be compiled and returned as a variable which can then be used to perform actions based on the collected information.  The following information is collected.

```json
{
  "cluster": {
    "nodes": [
          # Array of Cohesity Node Details
    ],
    "protection": {
      "jobs": [
        # Array of Job Details
      ],
      "policies": [
        # Array of Backup Policy Information
      ],
      "runs": [
        # Array of Backup executions
      ],
      "sources": {
        "GenericNas": [
          # Array of GenericNas Protection Sources
        ],
        "Physical": [
          # Array of Physical Protection Sources
        ],
        "VMware":  [
          # Array of VMware Protection Sources
        ],
      }
    },
    "storage_domains": [
          # Array of Cohesity Backup Storage Domains
    ],
  }
}
```

### Requirements
[top](#cohesity-facts)

* Cohesity Cluster running version 6.0 or higher
* Ansible >= 2.6
  * [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a unix system running any of the following operating systems: Linux (Red Hat, Debian, CentOS), macOS, any of the BSDs. Windows isn’t supported for the control machine.
* Python >= 2.6

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## SYNTAX
[top](#cohesity-facts)


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


## PARAMETERS
[top](#cohesity-facts)


| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity Cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster. Domain Specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |
|   | state | Choice | -**complete**<br>-minimal | Determines what the level of collection should be *complete* or *absent* from the Cluster.  If *complete*, then all data is collected automatically regardless of the specified inclusions excluding `include_deleted`. |
|   | include_sources | Boolean | False | Determines if the specified resource information should be collected. |
|   | include_jobs | Boolean | False | Determines if the specified resource information should be collected. |
|   | include_runs | Boolean | False | Determines if the specified resource information should be collected. |
|   | active_only | Boolean | False | Determines if only active jobs should be collected. |
|   | include_deleted | Boolean | False | Determines if results should include deleted items. |

## OUTPUTS
[top](#cohesity-facts)

```json
{
  "cluster": {
    "nodes": [
          # Array of Cohesity Node Details
    ],
    "protection": {
      "jobs": [
        # Array of Job Details
      ],
      "policies": [
        # Array of Backup Policy Information
      ],
      "runs": [
        # Array of Backup executions
      ],
      "sources": {
        "GenericNas": [
          # Array of GenericNas Protection Sources
        ],
        "Physical": [
          # Array of Physical Protection Sources
        ],
        "VMware":  [
          # Array of VMware Protection Sources
        ],
      }
    },
    "storage_domains": [
          # Array of Cohesity Backup Storage Domains
    ],
  }
}
```
