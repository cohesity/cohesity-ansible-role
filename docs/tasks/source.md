# Task: Cohesity Protection Source Management

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customizing your playbooks](#Customizing-your-playbooks)
  - [Creation of new Physical Protection Sources using the Ansible Inventory](#Creation-of-new-Physical-Protection-Sources-using-the-Ansible-Inventory)
  - [Creation of new VMware vCenter Protection Source](#Creation-of-new-VMware-vCenter-Protection-Source)
  - [Creation of new NFS Protection Source](#Creation-of-new-NFS-Protection-Source)
- [How the Task works](#How-the-Task-works)

## SYNOPSIS
[top](#task-cohesity-protection-source-management)

This task can be used to add and configure Cohesity Protection Sources

#### How it works
- The task starts by determining if the named endpoint exists in the cluster
- Upon validation, the task will create a new Protection Source (*state=present*) or remove the existing Protection Source (*state=absent*) from the Cluster.
> **IMPORTANT**!<br>
  When *state=absent*, there are no job validations nor state checks to ensure that backups are not running.  If jobs exist for the Source, an error will be raised and the task will fail.

### Requirements
[top](#task-cohesity-protection-source-management)

* Cohesity Cluster running version 6.0 or higher
* Ansible >= 2.6
  * [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a unix system running any of the following operating systems: Linux (Red Hat, Debian, CentOS), macOS, any of the BSDs. Windows isn’t supported for the control machine.
* Python >= 2.6

> **Notes**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using theis task, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-protection-source-management)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see the [official Cohesity Ansible module documentation](/modules/cohesity_source.md?id=syntax)
```yaml
cohesity_source:
  state: present
  endpoint: ""
  environment: ""
  host_type: ""
  vmware_type: ""
  source_username: ""
  source_password: ""
  nas_protocol: ""
  nas_username: ""
  nas_password: ""
```
## Customizing your playbooks
[top](#task-cohesity-protection-source-management)

This example show how to include the Cohesity-Ansible role in your custom playbooks and leverage this task as part of the delivery.

### Creation of new Physical Protection Sources using the Ansible Inventory
[top](#task-cohesity-protection-source-management)

Here is an example playbook that creates new Protection Sources for all Linux hosts based on the registered inventory hostname. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    gather_facts: no
    roles:
        - cohesity.ansible
    tasks:
      - name: Configure Cohesity Protection Source on each Linux Physical Server
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: present
                endpoint: "{{ hostvars[item]['ansible_host'] }}"
                host_type: "Linux"
        with_items: "{{ groups.linux }}"
        tags: [ 'cohesity', 'sources', 'register', 'linux' ]
```

### Creation of new VMware vCenter Protection Source
[top](#task-cohesity-protection-source-management)

Here is an example playbook that creates new Protection Sources for the chosen vCenter host. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
        var_vcenter_server: myvcenter.cohesity.lab
        var_vcenter_username: administrator
        var_vcenter_password: secret
    gather_facts: no
    roles:
        - cohesity.ansible
    tasks:
      - name: Configure Cohesity Protection Source on VMware vCenter Host
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: present
                endpoint: "{{var_vcenter_server }}"
                environment: "VMware"
                vmware_type: "VCenter"
                source_username: "{{ var_vcenter_username }}"
                source_password: "{{ var_vcenter_password }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]
```

### Creation of new NFS Protection Source
[top](#task-cohesity-protection-source-management)

Here is an example playbook that creates new Protection Sources for the chosen vCenter host. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
        var_export_path: 10.2.x.x:/export_path
        var_vcenter_username: administrator
        var_vcenter_password: secret
    gather_facts: no
    roles:
        - cohesity.ansible
    tasks:
      - name: Configure Cohesity Protection Source on NFS Export
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: present
                endpoint: "{{ var_export_path }}"
                environment: "GenericNAS"
                nas_protocol: "NFS"
        tags: [ 'cohesity', 'sources', 'register', 'nfs' ]
```


## How the Task works
[top](#task-cohesity-protection-source-management)

The following information is copied directly from the included task in this role.  The source file can be found at the root of this repo in `/tasks/source.yml`
```yaml
---
- name: "Cohesity Protection Source: Set {{ cohesity_source.endpoint | default('endpoint') }} to state of {{ cohesity_source.state | default('present') }}"
  cohesity_source:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs }}"
    state:  "{{ cohesity_source.state | default('present') }}"
    endpoint: "{{ cohesity_source.endpoint | default('') }}"
    environment: "{{ cohesity_source.environment | default('Physical') }}"
    host_type: "{{ cohesity_source.host_type | default('Linux') }}"
    vmware_type: "{{ cohesity_source.vmware_type | default('VCenter') }}"
    source_username: "{{ cohesity_source.source_username | default('') }}"
    source_password: "{{ cohesity_source.source_password | default('') }}"
    nas_protocol: "{{ cohesity_source.nas_protocol | default('NFS') }}"
    nas_username: "{{ cohesity_source.nas_username | default('') }}"
    nas_password: "{{ cohesity_source.nas_password | default('') }}"
  tags: always

```