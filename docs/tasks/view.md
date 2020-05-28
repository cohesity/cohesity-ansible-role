# Task: Cohesity View Management

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Create a view with protocol access to NFS, SMB, and S3](#Create-a-view-with-protocol-access-to-NFS,-SMB,-and-S3)
  - [Update a view with protocol access to NFS, SMB, and S3 to NFS only](#Update-a-view-with-protocol-access-to-NFS,-SMB,-and-S3-to-NFS-only)
  - [Delete a view](#Delete-a-view)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-cohesity-view-management)

Use this task to create, update and delete a Cohesity view.

#### How It Works
- The task checks if a view with given name already exists. If it exists, it updates the existing view when state is **present** and deletes the view when the state is **absent**
- The task creates a view if the state is **present** and a view with the given name doesn't exist.

### Requirements
[top](#task-cohesity-view-management)

* Cohesity DataPlatform running version 6.4 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher
* [Python Management SDK](https://developer.cohesity.com/apidocs-641.html#/python/getting-started)

> **Notes:**
  - Before using this task, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-view-management)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see [Cohesity View](../library/cohesity_view.md).
```yaml
cohesity_view:
  state: 
  name: 
  description: 
  storage_domain:
  qos_policy: 
  protocol: 
  case_insensitive: 
  object_key_pattern: 
  inline_dedupe_compression: 
  security:
  quota: 
  nfs_options: 
  smb_options: 
```
## Customize Your Playbooks
[top](#task-cohesity-view-management)

This example shows how to include the Cohesity Ansible role in your custom playbooks and leverage this task.

### Create a view with protocol access to NFS, SMB, and S3
[top](#task-cohesity-view-management)

This is an example playbook that creates a Cohesity view. (Remember to change it to suit your environment.)

Following inventory file can be used for the ansible-playbook runs below. Copy the content to `inventory.ini` file
```ini
[workstation]
127.0.0.1 ansible_connection=local

```
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

You can create a file called `create_view.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> create_view.yml"
  ```

```yaml
---
  - hosts: workstation
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      - name: Create Cohesity view
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: view
        vars:
         cohesity_server: 10.22.11.132
         cohesity_admin: cohesity
         cohesity_password: password
         cohesity_view:
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
[top](#task-cohesity-view-management)

This is an example playbook used to update a view. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: workstation
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      - name: Update Cohesity view
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: view
        vars:
         cohesity_server: 10.22.11.132
         cohesity_admin: cohesity
         cohesity_password: password
         cohesity_view:
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
[top](#task-cohesity-view-management)

This is an example playbook that deletes a Cohesity view. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: workstation
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      - name: Delete Cohesity view
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: view
        vars:
         cohesity_server: 10.22.11.132
         cohesity_admin: cohesity
         cohesity_password: password
         cohesity_view:
              state: absent
              name: test_view
              storage_domain: DefaultStorageDomain
              case_insensitive: True
```


## How the Task Works
[top](#task-cohesity-view-management)

The following information is copied directly from the included task in this role. The source file is located at the root of this role in `/tasks/view.yml`.
```yaml
---
- name: "Cohesity view: Set {{ cohesity_view.name | default('view_name') }} to state of {{ cohesity_view.state | default('present') }}"
  cohesity_view:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    state: "{{ cohesity_view.state | default('present') }}"
    name: "{{ cohesity_view.name }}"
    description: "{{ cohesity_view.description | default('') }}"
    storage_domain: "{{ cohesity_view.storage_domain }}"
    qos_policy: "{{ cohesity_view.qos_policy | default('Backup Target Low') }}"
    protocol: "{{ cohesity_view.protocol | default('All') }}"
    case_insensitive: "{{ cohesity_view.case_insensitive | default(True) }}"
    object_key_pattern: "{{ cohesity_view.object_key_pattern | default('') }}"
    inline_dedupe_compression: "{{ cohesity_view.inline_dedupe_compression | default(False) }}"
    security: "{{ cohesity_view.security | default('') }}"
    quota: "{{ cohesity_view.quota | default('') }}"
    nfs_options: "{{ cohesity_view.nfs_options | default('') }}"
    smb_options: "{{ cohesity_view.smb_options | default('') }}"
  tags: always

```
