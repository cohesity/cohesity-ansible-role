# Cohesity Facts and Details

## SYNOPSIS
Ansible Module used to collect and compile details about a Cohesity Cluster.  The data can be compiled and returned as a variable which can then be used to perform actions based on the collected information.

### Requirements
  - A physical or virtual Cohesity system. The modules were developed with Cohesity version 6.1.0
  - Ansible 2.6
  - Python >= 2.6

### Notes
  - Currently, the Ansible Module requires Full Cluster Administrator access.

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
| X | **cluster** | String | | IP or FQDN for the Cohesity Cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |
|   | state | Choice | -**complete**<br>-minimal | Determines what the level of collection should be *complete* or *absent* from the Cluster.  If *complete*, then all data is collected automatically regardless of the specified inclusions excluding `include_deleted`. |
|   | include_sources | Boolean | False | Determines if the specified resource information should be collected. |
|   | include_jobs | Boolean | False | Determines if the specified resource information should be collected. |
|   | include_runs | Boolean | False | Determines if the specified resource information should be collected. |
|   | active_only | Boolean | False | Determines if only active jobs should be collected. |
|   | include_deleted | Boolean | False | Determines if results should include deleted items. |

## OUTPUTS
- N/A

