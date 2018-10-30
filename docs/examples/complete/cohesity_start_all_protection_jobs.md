# Cohesity start all registered Protection Jobs

## SYNOPSIS
This example play provides an example on how to leverage information collected using the `cohesity_facts` module to automatically discover all registered protection jobs and start each backup.
- The play will start by reading all data about the Cohesity Cluster and registering a new variable.
- For each registered Protection Job, a call will be made to start the backup.

Note: This play does not require that the jobs were created via the Ansible Integration as it will discover **all* backup jobs registered in the cluster.

### Requirements
  - A physical or virtual Cohesity system. The modules were developed with Cohesity version 6.1.0
  - Ansible 2.6
  - Python >= 2.6

### Notes
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Ansible Variables

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity Cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | var_validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |

## Working with Cohesity Facts module

This play leverages certain data collected as part of the `cohesity_facts` module distributed with the Cohesity.Ansible Role.  For more information [see our Guide on Cohesity Facts](../../modules/cohesity_facts.md)
