# Cohesity Protection Source

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Register a Physical Cohesity Protection Source on a selected Linux endpoint using Defaults](#Register-a-Physical-Cohesity-Protection-Source-on-a-selected-Linux-endpoint-using-Defaults)
  - [Register a Physical Cohesity Protection Source on a selected Windows endpoint](#Register-a-Physical-Cohesity-Protection-Source-on-a-selected-Windows-endpoint)
  - [Register a VMware Cohesity Protection Source on a selected endpoint](#Register-a-VMware-Cohesity-Protection-Source-on-a-selected-endpoint)
  - [Register a NAS Cohesity Protection Source on a selected NFS mountpoint](#Register-a-NAS-Cohesity-Protection-Source-on-a-selected-NFS-mountpoint)
  - [Register a NAS Cohesity Protection Source on a selected SMB share](#Register-a-NAS-Cohesity-Protection-Source-on-a-selected-SMB-share)
  - [Unegister an existing Cohesity Protection Source on a selected endpoint](#Unegister-an-existing-Cohesity-Protection-Source-on-a-selected-endpoint)
- [Parameters](#parameters)
- [Outputs](#outputs)
  - [Example return from a succesful registration of a Linux Physical Source](#Example-return-from-a-succesful-registration-of-a-Linux-Physical-Source)
  - [Example return from a succesful registration of a VMware Source](#Example-return-from-a-succesful-registration-of-a-VMware-Source)
  - [Example return from a succesful registration of a GenericNas Source](#Example-return-from-a-succesful-registration-of-a-GenericNas-Source)
  - [Example return from the succesful unregistration of a Protection Source](#Example-return-from-the-succesful-unregistration-of-a-Protection-Source)

## Synopsis
[top](#cohesity-protection-source)

The Ansible Module registers or removes Cohesity Protection Sources to/from a Cohesity Cluster.  When executed in a playbook, the Cohesity Protection Source will be validated and the appropriate state action will be applied.

### Requirements
[top](#cohesity-protection-source)

* Cohesity DataPlatform version 6.4.1 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-protection-source)

```yaml
- cohesity_source:
    cluster: <ip or hostname for cohesity cluster>
    username: <username with cluster level permissions>
    password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Protection Source>
    endpoint: <ip or hostname or nas_path to be configured as a Protection Source>
    environment: <protection source environment type>
    host_type: <physical protection OS type>
    physical_type: <physical protection platform type>
    source_username: <username for the Source connection>
    source_password: <password for the selected source_username>
    vmware_type: <vmware source protection type>
    nas_protocol: <selected nas_protocol for the source>
    nas_username: <username for the NAS Source connection>
    nas_password: <password for the selected nas_username>
    skip_validation: <flag to disable mount point validation during NAS registration process>
    nas_type: <type of a NAS Object>
    force_register: <boolean to determine if the source should be force_registered even if connection failed>
```

## Examples
[top](#cohesity-protection-source)

### Register a Physical Cohesity Protection Source on a selected Linux endpoint using Defaults
[top](#cohesity-protection-source)

```yaml
- cohesity_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: mylinux.host.lab
    environment: Physical
    state: present

```

### Register a Physical Cohesity Protection Source on a selected Windows endpoint
[top](#cohesity-protection-source)

```yaml
- cohesity_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: mywindows.host.lab
    environment: Physical
    host_type: Windows
    state: present

```

### Register a VMware Cohesity Protection Source on a selected endpoint
[top](#cohesity-protection-source)

```yaml
- cohesity_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: myvcenter.host.lab
    environment: VMware
    source_username: admin@vcenter.local
    source_password: vmware
    vmware_type: Vcenter
    state: present

```

### Register a NAS Cohesity Protection Source on a selected NFS mountpoint
[top](#cohesity-protection-source)

```yaml
- cohesity_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: mynfs.host.lab:/exports
    environment: GenericNas
    state: present

```

### Register a NAS Cohesity Protection Source on a selected SMB share
[top](#cohesity-protection-source)

```yaml
- cohesity_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: \\\\myfileserver.host.lab\\data
    environment: GenericNas
    nas_protocol: SMB
    nas_username: administrator
    nas_password: password
    state: present
```

### Unegister an existing Cohesity Protection Source on a selected endpoint
[top](#cohesity-protection-source)

```yaml
- cohesity_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: myvcenter.host.lab
    environment: VMware
    state: absent

```


## Parameters
[top](#cohesity-protection-source)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as.<br>- username@domain or domain/username (will be deprecated in future). |
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent | Determines the state of the Protection Source. |
| X | **endpoint** | String | | Specifies the network endpoint where the Protection Source is reachable. It can be the URL, hostname, IP address, NFS mount point, or SMB Share of the Protection Source. |
| X | **environment** | Choice | -VMware<br>-Physical<br>-GenericNas | Specifies the environment type (such as VMware or SQL) of the Protection Source this Job is protecting. |
|   | host_type | Choice | -**Linux**<br>-Windows<br>-Aix | Specifies the optional OS type of the Protection Source (such as *Windows* or *Linux*). *Linux* indicates the Linux operating system. *Windows* indicates the Microsoft Windows operating system. *Aix* indicates the IBM AIX operating system. Optional when *state=present* and *environment=Physical*.
|   | physical_type | Choice | -**Host**<br>-WindowsCluster | Specifies the entity type such as *Host* if the *environment=Physical*. *Host* indicates a single physical server. *WindowsCluster* indicates a Microsoft Windows cluster. Optional when *state=present* and *environment=Physical*.
|   | force_register | Boolean | False | When *True*, forces the registration of the Cohesity Protection Source. |
|   | vmware_type | Choice | -**VCenter**<br>-Folder<br>-Datacenter<br>-ComputeResource<br>-ClusterComputeResource<br>-ResourcePool<br>-Datastore<br>-HostSystem<br>-VirtualMachine<br>-VirtualApp<br>-StandaloneHost<br>-StoragePod<br>-Network<br>-DistributedVirtualPortgroup<br>-TagCategory<br>-Tag | Specifies the entity type such as *VCenter* if the environment is *VMware*. |
|   | source_username | String | | Specifies username to access the target source. **Required** when *state=present* and *environment=VMware* |
|   | source_password | String | | Specifies the password to access the target source. This parameter will not be logged. **Required** when *state=present* and *environment=VMware* |
|   | nas_protocol | Choice | -**NFS**<br>-SMB | Specifies the type of connection for the NAS Mountpoint. SMB Share paths must be in \\\\server\\share format. **Required** when *state=present* and *environment=GenericNas* |
|   | nas_username | String |  | Specifies username to access the target NAS Environment. Supported Format is Username or username@domain or Domain/username (will be deprecated in future). **Required** when *state=present* and *environment=GenericNas* and *nas_protocol=SMB* |
|   | nas_password | String | | Specifies the password to access the target NAS Environment. This parameter is not logged. Required when *state=present* and *environment=GenericNas* and *nas_protocol=SMB* |
|   | nas_type | Choice | -**Host**<br>-**Group** | Specifies the type of a NAS Object|
|   | skip_validation | Boolean | False | Specifies the flag to disable mount point validation during registration process|

## Outputs
[top](#cohesity-protection-source)

>**Note:**
 - Data returned from the Cohesity API is often prepended with a 'k' such as 'kVMware' or 'kPhysical'.  To adhere to these standards, the Cohesity Ansible module returns these values exactly.

### Example return from a succesful registration of a Linux Physical Source
[top](#cohesity-protection-source)

```json
{
  "ProtectionSource": {
    "hostType": "kLinux",
    "id": {
      "clusterId": 8621173906188849,
      "clusterIncarnationId": 1538852526333,
      "id": 240
    },
    "name": "10.2.55.72",
    "type": "kHost"
  },
  "changed": true,
  "item": "control",
  "msg": "Registration of Cohesity Protection Source Complete"
}
```

### Example return from a succesful registration of a VMware Source
[top](#cohesity-protection-source)

```json
{
  "ProtectionSource": {
    "id": {
      "uuid": "ebd9bfce-b845-4aa3-842a-3f0dc381bbab"
    },
    "name": "vc-67.eco.eng.cohesity.com",
    "type": "kVCenter"
  },
  "changed": true,
  "msg": "Registration of Cohesity Protection Source Complete"
}
```

### Example return from a succesful registration of a GenericNas Source
[top](#cohesity-protection-source)

```json
{
  "ProtectionSource ": {
    "environment ": "kGenericNas ",
    "id": 396,
    "name ": "10.2.145.19:/export_path",
    "path": "10.2.145.19:/export_path",
    "protocol ": "NFS"
  }
}
```

### Example return from the succesful unregistration of a Protection Source
[top](#cohesity-protection-source)

```json
{
  "changed": true,
  "id": 241,
  "endpoint": "mylinux.host.lab"
  "msg": "Unregistration of Cohesity Protection Source Complete"
}
```
