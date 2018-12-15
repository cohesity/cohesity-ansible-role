# Cohesity Protection Source

## SYNOPSIS
Ansible Module used to register or remove the Cohesity Protection Sources to/from a Cohesity Cluster.  When executed in a playbook, the Cohesity Protection Source will be validated and the appropriate state action will be applied.

### Requirements
* Cohesity Cluster running version 6.0 or higher
* Ansible >= 2.6
  * [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a unix system running any of the following operating systems: Linux (Red Hat, Debian, CentOS), macOS, any of the BSDs. Windows isn’t supported for the control machine.
* Python >= 2.6

### Notes
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## SYNTAX

```yaml
- cohesity_source:
    server: <ip or hostname for cohesity cluster>
    cohesity_admin: <username with cluster level permissions>
    cohesity_password: <password for the selected user>
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
    force_register: <boolean to determine if the source should be force_registered even if connection failed>
```

## EXAMPLES

```yaml
# Register a Physical Cohesity Protection Source on a selected Linux endpoint using Defaults
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: mylinux.host.lab
    state: present

# Register a Physical Cohesity Protection Source on a selected Windows endpoint
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: mywindows.host.lab
    environment: Physical
    host_type: Windows
    state: present

# Register a VMware Cohesity Protection Source on a selected endpoint
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: myvcenter.host.lab
    environment: VMware
    source_username: admin@vcenter.local
    source_password: vmware
    vmware_type: Vcenter
    state: present

# Register a NAS Cohesity Protection Source on a selected NFS mountpoint
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: mynfs.host.lab:/exports
    environment: GenericNas
    state: present

# Register a NAS Cohesity Protection Source on a selected SMB share
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: \\\\myfileserver.host.lab\\data
    environment: GenericNas
    nas_protocol: SMB
    nas_username: administrator
    nas_password: password
    state: present

# Unegister an existing Cohesity Protection Source on a selected endpoint
- cohesity_source:
    server: cohesity.lab
    username: admin
    password: password
    endpoint: myvcenter.host.lab
    environment: VMware
    state: absent

```


## PARAMETERS

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity Cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster. Domain Specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |
|   | state | Choice | -**present**<br>-absent | Determines the state of the Protection Source. |
| X | **endpoint** | String | | Specifies the network endpoint of the Protection Source where it is reachable. It could be an URL or hostname or an IP address of the Protection Source or a NAS Share/Export Path. |
| X | **environment** | Choice | -VMware<br>-Physical<br>-GenericNas | Specifies the environment type (such as VMware or SQL) of the Protection Source this Job is protecting. |
|   | host_type | Choice | -**Linux**<br>-Windows<br>-Aix | Specifies the optional OS type of the Protection Source (such as *Windows* or *Linux*). *Linux* indicates the Linux operating system. *Windows* indicates the Microsoft Windows operating system. *Aix* indicates the IBM AIX operating system. Optional when *state=present* and *environment=Physical*.
|   | physical_type | Choice | -**Host**<br>-WindowsCluster | Specifies the entity type such as *Host* if the *environment=Physical*. *Host* indicates a single physical server. *WindowsCluster* indicates a Microsoft Windows cluster. Optional when *state=present* and *environment=Physical*.
|   | force_register | Boolean | False | Enabling this option will force the registration of the Cohesity Protection Source. |
|   | vmware_type | Choice | -**VCenter**<br>-Folder<br>-Datacenter<br>-ComputeResource<br>-ClusterComputeResource<br>-ResourcePool<br>-Datastore<br>-HostSystem<br>-VirtualMachine<br>-VirtualApp<br>-StandaloneHost<br>-StoragePod<br>-Network<br>-DistributedVirtualPortgroup<br>-TagCategory<br>-Tag | Specifies the entity type such as *VCenter* if the environment is *VMware*. |
|   | source_username | String | | Specifies username to access the target source. **Required** when *state=present* and *environment=VMware* |
|   | source_password | String | | Specifies the password to access the target source. This parameter will not be logged. **Required** when *state=present* and *environment=VMware* |
|   | nas_protocol | Choice | -**NFS**<br>-SMB | Specifies the type of connection for the NAS Mountpoint. SMB Share paths must be in \\\\server\\share format. **Required** when *state=present* and *environment=GenericNas* |
|   | nas_username | String |  | Specifies username to access the target NAS Environment. Supported Format is Username or Domain\\Username Required when *state=present* and *environment=GenericNas* and *nas_protocol=SMB* |
|   | nas_password | String | | Specifies the password to accessthe target NAS Environment. This parameter will not be logged. Required when *state=present* and *environment=GenericNas* and *nas_protocol=SMB* |

## OUTPUTS
- Returns the registered Protection Source ID

