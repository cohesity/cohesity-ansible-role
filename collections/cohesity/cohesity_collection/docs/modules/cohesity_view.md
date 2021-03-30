# Cohesity View

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Create a view with protocol access to NFS, SMB, and S3](#Create-a-view-with-protocol-access-to-NFS,-SMB,-and-S3)
  - [Update a view with protocol access to NFS, SMB, and S3 to NFS only](#Update-a-view-with-protocol-access-to-NFS,-SMB,-and-S3-to-NFS-only)
  - [Delete a view](#Delete-a-view)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-view)

The Ansible Module can be used to create, update and delete a view.

### Requirements
[top](#cohesity-view)

* Cohesity DataPlatform version 6.4 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher
* [Cohesity Management SDK](https://developer.cohesity.com/apidocs-641.html#/python/getting-started)

## Syntax
[top](#cohesity-view)

```yaml
- cohesity_view:
    cluster: <ip or hostname for cohesity cluster>
    username: <username with cluster level permissions>
    password: <password for the selected user>
    state: <state of the view>
    name: <name of the view>
    description: <description about the view>
    storage_domain: <specifies the storage domain>
    qos_policy: <name of the QoS policy used for the view>
    protocol: <supported protocols for the view>
    case_insensitive: <whether to support case insensitive file or folder names>
    object_key_pattern: <type of S3 key mapping config>
    inline_dedupe_compression: <whether to disable inline deduplication and compression or inherit from the storage domain>
    security: <dictionary with security and global subnet whitelist details>
    quota: <dictionary with logical quota policy details>
    nfs_options: <dictionary with nfs related settings>
    smb_options: <dictionary with smb related settings>
```

## Examples
[top](#cohesity-view)

### Create a view with protocol access to NFS, SMB, and S3
[top](#cohesity-view)

```yaml
- cohesity_view:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: test_view
    storage_domain: DefaultStorageDomain
    protocol: All
    case_insensitive: True
    description: This is an Ansible test view
    qos_policy: Backup Target High
    inline_dedupe_compression: False
    security:
       security_mode: NtfsMode
       override_global_whitelist: True
       whitelist:
         -  subnet_ip: "10.22.146.112"
            subnet_mask: "255.255.144.1"
            nfs_permission: "ReadOnly"
            smb_permission: "Disabled"
            nfs_root_squash: True
            description: "subnet 1"          
         -  subnet_ip: "10.22.146.113"
            subnet_mask: "255.255.144.1"
            nfs_permission: "ReadOnly"
            smb_permission: "ReadOnly"
            nfs_root_squash: False
            description: "subnet 2"
    quota:
      hard_limit_bytes: 900000
      alert_limit_bytes: 1000
      set_logical_quota: True
      set_alert_threshold: True
    nfs_options:
        view_discovery: True
        user_id: 100
        group_id: 2
    smb_options:
        view_discovery: True
        access_based_enumeration: False
```

### Update a view with protocol access to NFS, SMB, and S3 to NFS only
[top](#cohesity-view)

```yaml
- cohesity_view:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: test_view
    storage_domain: DefaultStorageDomain
    protocol: NFSOnly
    case_insensitive: True
    description: This is an Ansible test view
    qos_policy: Backup Target High
    inline_dedupe_compression: False
    security:
       override_global_whitelist: False
       whitelist:
         -  subnet_ip: "10.22.146.122"
            subnet_mask: "255.255.144.1"
            nfs_permission: "ReadOnly"
            smb_permission: "Disabled"
            nfs_root_squash: True
            description: "subnet 1"          
         -  subnet_ip: "10.22.146.123"
            subnet_mask: "255.255.144.1"
            nfs_permission: "Disabled"
            smb_permission: "Disabled"
            nfs_root_squash: False
            description: "subnet 2"
    quota:
      alert_limit_bytes: 1000
      set_alert_threshold: True
    nfs_options:
        view_discovery: False

```

### Delete a view
[top](#cohesity-view)

```yaml
- cohesity_view:
    cluster: cohesity.lab
    username: admin
    password: password
    state: absent
    name: test_view
    storage_domain: DefaultStorageDomain
    case_insensitive: True
```

## Parameters
[top](#cohesity-view)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as<br>- username@domain |
| X | **password** | String | | Password belonging to the selected username (password used to login to cluster from UI).  This parameter is not logged. |
|   | state | Choice | -**present**<br>-absent | Determines the state of the view. If the state is **present** the view is created and if the view already exists then the view is updated. If the state is **absent** the view is deleted |
| X | **name** | String | | Specifies the name of the view. |
|   | description | String | | Specifies a description about the view.|
| X | **storage_domain** |  |  | Specifies the storage domain.|
|   | protocol | Choice | -**All**<br>-NFSOnly<br>-SMBOnly<br>-S3Only | Specifies the supported protocols for the view. |
|   | qos_policy| Choice | -**Backup Target Low**<br>-Backup Target High<br>-Backup Target SSD<br>-Backup Target CommVault<br>-**TestAndDev Low**<br>-TestAndDev High| Specifies the name of the QoS policy used for the view|
| X | case_insensitive | Boolean | | Specifies whether to support case insensitive files or folder names. This parameter can only be set during view creation and cannot be changed later|
|  | object_key_pattern | Choice | -Random<br>-Short<br>-Long<br>-Hierarchical | Specifies the type of S3 key mapping configuration. Applicable and required only when protocol is **S3Only** |
|  | inline_dedupe_compression | Boolean | False | If **false**, the inline deduplication and compression settings inherited from the storage domain applies to this view. If **true**, both inline deduplication and compression are disabled for this view. This can only be set to **true** if inline deduplication is set for the storage domain.|
|   | security | Dictionary | | A dictionary with **security_mode**, **override_global_whitelist**, **whitelist** keys. The keys are described below |
|   | security_mode | Choice | -**NativeMode**<br>-UnifiedMode<br>-NtfsMode | Specifies the security mode used for this view. Applicable only when protocol is **All** . This is a key in **security** parameter|
|   | override_global_whitelist | Boolean | | When this parameter is set (True or False), an array of subnet whitelist is expected. When set to **True** view level client subnet whitelist overrides cluster and global settings. When set to **False** view level client subnet whitelist extends cluster and global settings. This is a key in **security** parameter| 
|   | whitelist | Array | | Specifies a list of dictionaries with subnet details. This is a key in **security** parameter. The dictionary has **subnet_ip**, **subnet_mask**, **nfs_permission**, **smb_permission**, **nfs_root_squash**, **description** keys. The keys are described below |
|   | subnet_ip | String | | Specifies either an IPv6 address or an IPv4 address. **Required** when whitelist is set. This is a key in the **whitelist** element |
|   | subnet_mask | String | | Specifies the netmask using an IP4 address. The netmask can only be set using netmaskIp4 if the IP address is an IPv4 address. **Required** when whitelist is set.  This is a key in the **whitelist** element |
|   | nfs_permission | Choice | -**ReadWrite**<br>-ReadOnly<br>-Disabled |  Indicates protocol access level. This is a key in the **whitelist** element|
|   | smb_permission | Choice | -**ReadWrite**<br>-ReadOnly<br>-Disabled |  Indicates protocol access level. This is a key in the **whitelist** element |
|   | nfs_root_squash | Boolean | False | Specifies whether clients from this subnet can mount as root on NFS. This is a key in the **whitelist** element |
|   | description | String | | Description of the subnet. This is a key in the **whitelist** element |
|   | quota | Dictionary | | Specifies the logical quota policy on the view. The dictionary has **set_logical_quota**, **set_alert_threshold**, **hard_limit_bytes**, **alert_limit_bytes** keys. The keys are described below. |
|   | set_logical_quota | Boolean | False | Specifies whether to set quota limit for the view. This is a key in **quota** parameter. |
|   | set_alert_threshold | Boolean | False | Specifies whether to set quota limit on when an alert should be triggered. This is a key in **quota** parameter. |
|   | hard_limit_bytes | Integer | 20 GiB | Specifies the quota limit in bytes allowed for this view. This is applied only when **set_logical_quota** is set to **True**. This is a key in **quota** parameter |
|   | alert_limit_bytes | Integer | 18 GiB | Specifies the quota limit in bytes when an alert should be triggerd. This is applied only when **set_alert_threshold** is set to **True**. This is a key in **quota** parameter|
|   | nfs_options | Dictionary | | Specifies NFS related settings. It expects **view_discovery**, **user_id**, **group_id** keys. The keys are described below.|
|   | view_discovery | Boolean | True | If set, it enables discovery of view for NFS. This is a key in **nfs_options** parameter|
|   | user_id | Integer | 0 | Unix UID for the root of the file system. This is a key in **nfs_options** parameter |
|   | group_id | Integer | 0 | Unix GID for the root of the file system. This is a key in **nfs_options** parameter |
|   | smb_options | Dictionary | | Specifies NFS related settings. It expects **view_discovery**, **access_based_enumeration** keys. The keys are described below.|
|   | view_discovery | Boolean | True | If set, it enables discovery of view for SMB. This is a key in **smb_options** parameter.|
|   | access_based_enumeration | Boolean | False | Specifies if access-based enumeration should be enabled. If **true**, only files and folders that the user has permissions to access are visible on the SMB share for that user. This is a key in **smb_options** parameter.|

## Outputs
[top](#cohesity-view)

- Returns view id and name
