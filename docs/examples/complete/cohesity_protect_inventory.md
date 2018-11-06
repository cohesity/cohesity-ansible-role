# Cohesity Full Protection using Ansible Inventory

## SYNOPSIS
This example play can help to accelerate the usage of the Cohesity Ansible integration by generating a full stack deployment of Cohesity Agents, Sources, and Jobs automatically.
- The play will start by reading all Physical servers from the Ansible Inventory and installing the agent.
- Upon completion of the agent installation, each Protection Source will be registered based on environment type:
  - Physical
  - VMware
  - GenericNas
- The final step will be to create a new Protection job for each of the Protection Sources.

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
