# Cohesity Agent Management - Windows

## SYNOPSIS
The Ansible Module deploys or removes the Cohesity Physical Agent from supported Windows Machines. When executed in a playbook, the Cohesity Agent installation is validated and the appropriate state action is applied. The most recent version of the Cohesity Agent is automatically downloaded to the host.

### Requirements
* Cohesity Dataplatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Powershell version 4.0 or higher

> **Tip:**  Currently, the Ansible Module requires Full Cluster Administrator access.

## SYNTAX

```yaml
- cohesity_win_agent:
    server: <ip or hostname for cohesity cluster>
    cohesity_admin: <username with cluster level permissions>
    cohesity_password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Agent>
    service_user: <username underwhich the service will run>
    service_password: <password for the selected service_user>
    install_type: <configure the installation type for the windows agent>
    preservesettings: <boolean to determine if the settings be retained when uninstalling the Cohesity Agent>
```

## EXAMPLES

```yaml
# Install the current version of the agent on Windows
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present

# Install the current version of the agent with custom Service Username/Password
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    service_user: cagent
    service_password: cagent

# Install the current version of the agent using FileSystem ChangeBlockTracker
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    install_type: fscbt

# Remove the current installed version of the agent
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: absent
```


## PARAMETERS

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster. Domain-specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent | Determines whether the agent is *present* or *absent* from the host. |
|   | service_user | String | | Username under which the Cohesity Agent is installed and run. This user must exist. |
|   | service_password | String | | Password belonging to the selected *service_user*.  This parameter is not logged. |
|   | install_type | Choice | -**volcbt**<br>-fscbt<br>-allcbt<br>-onlyagent | Installation type for the Cohesity Agent on Windows. |
|   | preservesettings | Boolean | False | Determines whether the settings are retained when uninstalling the Cohesity Agent. |
|   | reboot | Boolean | False | Determines whether the host is rebooted when installing the Cohesity Agent. |


## OUTPUTS
- N/A

