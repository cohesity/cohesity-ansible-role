# Cohesity Agent Management - Windows

[Go back to Documentation home page ](../README.md)

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

## Synopsis
[top](#cohesity-agent-management---windows)

The Ansible Module deploys or removes the Cohesity Physical Agent from supported Windows Machines. When executed in a playbook, the Cohesity Agent installation is validated and the appropriate state action is applied. The most recent version of the Cohesity Agent is automatically downloaded to the host.

### Requirements
[top](#cohesity-agent-management---windows)

* Cohesity Dataplatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Powershell version 4.0 or higher
* Agent installation is supported only on the operating systems listed on https://docs.cohesity.com where select your `DataPlatform` version -> `Release Notes` -> `Supported Software` -> `Physical Servers` section

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Cohesity Agent installation on Windows supports two types of Agent installation: <br>- filecbt<br>- **volcbt**†<br>- **allcbt**†<br>- onlyagent<br><br>**†** When you select type **volcbt** or **allcbt**, you will have to reboot the Windows server to complete the installation.

## Syntax
[top](#cohesity-agent-management---windows)

```yaml
- cohesity_win_agent:
    cluster: <ip or hostname for cohesity cluster>
    username: <username with cluster level permissions>
    password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Agent>
    service_user: <username underwhich the service will run>
    service_password: <password for the selected service_user>
    install_type: <configure the installation type for the windows agent>
    preservesettings: <boolean to determine if the settings be retained when uninstalling the Cohesity Agent>
```

## Examples
[top](#cohesity-agent-management---windows)

### Install the current version of the agent on Windows
[top](#cohesity-agent-management---windows)

```yaml
- cohesity_win_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
```

### Install the current version of the agent with custom Service Username/Password
[top](#cohesity-agent-management---windows)

```yaml
- cohesity_win_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    service_user: cagent
    service_password: cagent
```

### Install the current version of the agent using FileSystem ChangeBlockTracker
[top](#cohesity-agent-management---windows)

```yaml
- cohesity_win_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    install_type: fscbt
```

### Remove the current installed version of the agent
[top](#cohesity-agent-management---windows)

```yaml
- cohesity_win_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: absent
```


## Parameters
[top](#cohesity-agent-management---windows)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as <br>- username@domain or domain/username (will be deprecated in future).|
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent | Determines whether the agent is *present* or *absent* from the host. |
|   | service_user | String | | Username under which the Cohesity Agent is installed and run. This user must exist. |
|   | service_password | String | | Password belonging to the selected *service_user*.  This parameter is not logged. |
|   | install_type | Choice | -**volcbt**<br>-fscbt<br>-allcbt<br>-onlyagent | Installation type for the Cohesity Agent on Windows. |
|   | preservesettings | Boolean | False | Determines whether the settings are retained when uninstalling the Cohesity Agent. |
|   | reboot | Boolean | False | Determines whether the host is rebooted when installing the Cohesity Agent. |


## Outputs
[top](#cohesity-agent-management---windows)
- N/A

