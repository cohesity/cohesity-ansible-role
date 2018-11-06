# Cohesity Agent removal and installation using Ansible Inventory

## SYNOPSIS
This example play leverages the Ansible Inventory to dynamically remove and install the Ansible Agent on supported Physical platforms.
- The play will start by reading all Physical Linux servers from the Ansible Inventory and removing the agent.
- Upon completion of the agent removal, the current version of the agent will be installed.
- The next step will be to perform the uninstallation of the Agent on Windows systems followed by a mandatory reboot of the server.
- Once the reboot is complete, the current version of the agent will be install on the Windows servers.
- If the windows install_type is *volcbt* then a reboot of the windows servers will be triggered.

NOTE: This example play should be considered for demo purposes only.  This will connect to all Physical Linux and Windows servers and remove the agent.  There are no job validations nor state checks to ensure that backups are not running.  Also, all Windows servers will be rebooted at least once as part of the uninstallation procedure.

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
