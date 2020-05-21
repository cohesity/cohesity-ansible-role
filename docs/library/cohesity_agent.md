# Cohesity Agent Management - Linux

[Go back to Documentation home page ](../README.md)

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
  - [Install the current version of agent on Linux using native installers](#Install-the-current-version-of-agent-on-Linux-using-native-installers)
  - [Install the agent from custom download uri](#Install-the-agent-from-custom-download-uri)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-agent-management---linux)

The Ansible Module deploys or removes the Cohesity Physical Agent from supported Linux Machines. When executed in a playbook, the Cohesity Agent installation is validated and the appropriate state action is applied. The most recent version of the Cohesity Agent is automatically downloaded to the host.

### Requirements
[top](#cohesity-agent-management---linux)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - When using the default download location, the Cohesity agent installer is placed in `/tmp/<temp-dir`.  If your environment prevents the use of `/tmp` with a `noexec` option, then you must set an alternate location.

## Syntax
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: <ip or hostname for cohesity cluster>
    username: <cohesity username with cluster level permissions>
    password: <cohesity password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Agent>
    service_user: <username underwhich the service will run>
    service_group: <group underwhich the service will be owned>
    create_user: <boolean to determine if the service_user and service_group should be created>
    download_location: <optional path to which the installer will be downloaded>
    file_based: <boolean to determine if the agent install will be in non-LVM mode and support only file based backups
    native_package: <boolean to determine if a native or script based installer is used for agent installation>
    download_uri: <uri to download the agent installer from, if downloading the agent from custom location is preferred>
    operating_system: <the operating system on which the agent is installed>
```

## Examples
[top](#cohesity-agent-management---linux)

### Install the current version of the agent on Linux
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
```

### Install the current version of the agent on Linux using LDAP credentials
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: cohesity.lab
    username: demo/administrator
    password: password
    state: present
```

### Install the current version of the agent on Linux in Non-LVM mode
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    file_based: True
```

### Install the current version of the agent with custom User and Group
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    service_user: cagent
    service_group: cagent
    create_user: True
```

### Remove the current installed agent from the host
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    state: absent
```

### Download the agent installer to a custom location
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    download_location: /software/installers
    state: present
```

### Install the current version of agent on Linux using native installers
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    cluster: cohesity.lab
    username: admin
    password: password
    download_location: /software/installers
    state: present
    service_user: cohesity_user
    native_package: True
    operating_system: Ubuntu
```

### Install the agent from custom download uri
[top](#cohesity-agent-management---linux)

```yaml
- cohesity_agent:
    download_location: /software/installers
    state: present
    native_package: True
    service_user: cohesity_user
    download_uri: http://10.22.108.7/files/bin/installers/el-cohesity-agent-6.3-1.x86_64.rpm
    operating_system: CentOS
```


## Parameters
[top](#cohesity-agent-management---linux)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster. Not required if *download_uri* is given. |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as<br>- Domain/username. Not required if *download_uri* is given.|
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. Not required if *download_uri* is given.|
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. Not required if *download_uri* is given. |
|   | state | Choice | -**present**<br>-absent | Determines whether the agent is *present* or *absent* from the host. |
|   | service_user | String | cohesityagent | Username under which the Cohesity Agent is installed and run. This user must exist unless _create_user=**True**_ is also configured. For native installations i.e when native_package is enabled, this is a required parameter and the user must exist on the machine|
|   | service_group | String | cohesityagent | Group under which permissions are set for the Cohesity Agent configuration. This group must exist unless _create_user=**True**_ is also configured. This parameter does not apply when native_package is enabled i.e for native installations|
|   | create_user | Boolean | True | When enabled, this creates a new user and group based on the values of *service_user* and *service_group*. This parameter does not apply when native_package is enabled i.e for native installations|
|   | download_location | String |  | Optional directory path to which the installer is downloaded. If not selected, then a temporary directory is created in the default System Temp Directory. If you choose an alternate directory, the directory and installer will not be deleted at the end of the execution. |
|   | file_based | Boolean | False | When enabled, this installs the agent in non-LVM mode and supports only file based backups. |
|   | native_package | Boolean | False | When enabled, native installers are used for agent installation. If agent is installed using a native package, then agent uninstallation should also be done using native package i.e if **state=absent** then **native_package=True**|
|   | download_uri | String | | URI to download the agent, if downloading the installer from custom location is preferred. If specified the cluster credentials are not required. |
|   | operating_system | String| -CentOS <br> -Ubuntu <br> -RedHat | The operating sytem on which the agent is installed. Required only when **native_package** is **True**

## Outputs
[top](#cohesity-agent-management---linux)
- N/A

