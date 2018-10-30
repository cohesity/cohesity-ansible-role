# Cohesity Jobs management and creation using Ansible Inventory

## SYNOPSIS
This example play leverages the Ansible Inventory to dynamically manage and create Protection Jobs for existing Protection Sources.
- The play will start by reading all environments from the Ansible Inventory and cancel the corresponding Protection Job if active.
- Upon completion of the job stop, the job will be deleted **including all backups**.
- After the job is successfully removed, each source will be registered as a new Protection Job with the corresponding endpoint as the name of the Job created..

NOTE: This example play should be considered for demo purposes only.  This will remove and then register all Physical, VMware, and GenericNAS Protection Jobs based on the Ansible Inventory.  This action will **delete all backups** as part of the process.

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

## Ansible Inventory Configuration

To fully leverage this Ansible Play, you must configure your Ansible Inventory file with certain keys and values.  This allows for a much easier management of the overall experience.  For more information [see our Guide on Configuring your Ansible Inventory](../configuring-your-ansible-inventory.md)
