# Cohesity Agent Management - Linux

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Install the current version of the agent on Linux](#Install-the-current-version-of-the-agent-on-Linux)
  - [Install the current version of the agent on Linux using LDAP credentials](#Install-the-current-version-of-the-agent-on-Linux-using-LDAP-credentials)
  - [Install the current version of the agent on Linux in Non-LVM mode](#Install-the-current-version-of-the-agent-on-Linux-in-Non-LVM-mode)
  - [Install the current version of the agent with custom User and Group](#Install-the-current-version-of-the-agent-with-custom-User-and-Group)
  - [Remove the current installed agent from the host](#Remove-the-current-installed-agent-from-the-host)
  - [Download the agent installer to a custom location](#Download-the-agent-installer-to-a-custom-location)
- [Parameters](#parameters)
- [Outputs](#outputs)

## SYNOPSIS
[top](#cohesity-agent-management-linux)

The Ansible Module deploys or removes the Cohesity Physical Agent from supported Linux Machines. When executed in a playbook, the Cohesity Agent installation is validated and the appropriate state action is applied. The most recent version of the Cohesity Agent is automatically downloaded to the host.

### Requirements
[top](#cohesity-agent-management-linux)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - When using the default download location, the Cohesity agent installer will be place in `/tmp/<temp-dir` location.  If your environment prevents the use of `/tmp` with a `noexec` option, then the alternate location must be set.

## SYNTAX
[top](#cohesity-agent-management-linux)

```yaml
- cohesity_agent:
    server: <ip or hostname for cohesity cluster>
    cohesity_admin: <username with cluster level permissions>
    cohesity_password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Agent>
    service_user: <username underwhich the service will run>
    service_group: <group underwhich the service will be owned>
    create_user: <boolean to determine if the service_user and service_group should be created>
    download_location: <optional path to which the installer will be downloaded>
    file_based: <boolean to determine if the agent install will be in non-LVM mode and support only file based backups
```

## EXAMPLES
[top](#cohesity-agent-management-linux)

### Install the current version of the agent on Linux
[top](#cohesity-agent-management-linux)

```yaml
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present
```

### Install the current version of the agent on Linux using LDAP credentials
[top](#cohesity-agent-management-linux)

```yaml
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: demo\\administrator
    cohesity_password: password
    state: present
```

### Install the current version of the agent on Linux in Non-LVM mode
[top](#cohesity-agent-management-linux)

```yaml
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present
    file_based: True
```

### Install the current version of the agent with custom User and Group
[top](#cohesity-agent-management-linux)

```yaml
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present
    service_user: cagent
    service_group: cagent
    create_user: True
```

### Remove the current installed agent from the host
[top](#cohesity-agent-management-linux)

```yaml
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: absent
```

### Download the agent installer to a custom location
[top](#cohesity-agent-management-linux)

```yaml
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    download_location: /software/installers
    state: present
```


## PARAMETERS
[top](#cohesity-agent-management-linux)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity Cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster. Domain-specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent | Determines whether the agent is *present* or *absent* from the host. |
|   | service_user | String | cohesityagent | Username under which the Cohesity Agent is installed and run. This user must exist unless _create_user=**True**_ is also configured. |
|   | service_group | String | cohesityagent | Group under which permissions are set for the Cohesity Agent configuration. This group must exist unless _create_user=**True**_ is also configured. |
|   | create_user | Boolean | True | When enabled, this creates a new user and group based on the values of *service_user* and *service_group*. |
|   | download_location: | String |  | Optional directory path to which the installer is downloaded. If not selected, then a temporary directory is created in the default System Temp Directory. If you choose an alternate directory, the directory and installer will not be deleted at the end of the execution. |
|   | file_based | Boolean | False | When enabled, this installs the agent in non-LVM mode and supports only file based backups. |

## OUTPUTS
- N/A

