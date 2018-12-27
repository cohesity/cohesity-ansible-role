# Cohesity Agent Management - Windows

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Install the current version of the agent on Windows](#Install-the-current-version-of-the-agent-on-Windows)
  - [Install the current version of the agent with custom Service Username/Password](#Install-the-current-version-of-the-agent-with-custom-Service-UsernamePassword)
  - [Install the current version of the agent using FileSystem ChangeBlockTracker](#Install-the-current-version-of-the-agent-using-FileSystem-ChangeBlockTracker)
  - [Remove the current installed version of the agent](#Remove-the-current-installed-version-of-the-agent)
- [Parameters](#parameters)
- [Outputs](#outputs)

## SYNOPSIS
[top](#cohesity-agent-management-windows)

Ansible Module used to deploy or remove the Cohesity Physical Agent from supported Windows Machines.  When executed in a playbook, the Cohesity Agent installation will be validated and the appropriate state action will be applied.  The most recent version of the Cohesity Agent will be automatically downloaded to the host.

### Requirements
[top](#cohesity-agent-management-windows)

* Cohesity Cluster running version 6.0 or higher
* Ansible >= 2.6
  * [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a unix system running any of the following operating systems: Linux (Red Hat, Debian, CentOS), macOS, any of the BSDs. Windows isn’t supported for the control machine.
* Powershell >= 4.0

> **Notes**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Cohesity Agent installation on Windows supports two types of Agent install types: <br>- filecbt<br>- **volcbt***<br>- **allcbt***<br>- onlyagent<br>**\*** When installing or removing the agent and selecting either **volcbt** or **allcbt** type, a reboot of the Windows server must be performed to complete the action.

## SYNTAX
[top](#cohesity-agent-management-windows)

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
[top](#cohesity-agent-management-windows)

### Install the current version of the agent on Windows
[top](#cohesity-agent-management-windows)

```yaml
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
```

### Install the current version of the agent with custom Service Username/Password
[top](#cohesity-agent-management-windows)

```yaml
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    service_user: cagent
    service_password: cagent
```

### Install the current version of the agent using FileSystem ChangeBlockTracker
[top](#cohesity-agent-management-windows)

```yaml
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: present
    install_type: fscbt
```

### Remove the current installed version of the agent
[top](#cohesity-agent-management-windows)

```yaml
- cohesity_win_agent:
    server: cohesity.lab
    username: admin
    password: password
    state: absent
```


## PARAMETERS
[top](#cohesity-agent-management-windows)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity Cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster. Domain Specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |
|   | state | Choice | -**present**<br>-absent | Determines if the agent should be *present* or *absent* from the host |
|   | service_user | String | | Username underwhich the Cohesity Agent will be installed and run. This user must exist. |
|   | service_password | String | | Password belonging to the selected Service_Username.  This parameter will not be logged. |
|   | install_type | Choice | -**volcbt**<br>-fscbt<br>-allcbt<br>-onlyagent | Installation type for the Cohesity Agent on Windows |
|   | preservesettings | Boolean | False | Should the settings be retained when uninstalling the Cohesity Agent. |


## OUTPUTS
[top](#cohesity-agent-management-windows)

- N/A

