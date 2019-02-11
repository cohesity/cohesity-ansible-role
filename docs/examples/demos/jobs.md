# Create and Manage Cohesity Jobs Using Ansible Inventory

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Customize Your Playbooks](#Customize-Your-Playbooks)
  - [Register Protection Jobs for all hosts in the inventory](#Register-Protection-Jobs-for-all-hosts-in-the-inventory)
  - [Remove Protection Jobs for all hosts in the inventory](#Remove-Protection-Jobs-for-all-hosts-in-the-inventory)

## Synopsis
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

This example play leverages the Ansible Inventory to dynamically remove and create Protection Jobs for existing Protection Sources.  The source file for this playbook is located at the root of the role in `examples/demos/jobs.yml`.
> **IMPORTANT**!<br>
  This example play should be considered for demo purposes only.  This play removes and then registers all Physical, VMware, and GenericNAS Protection Jobs based on the Ansible Inventory.  There are no job validations or state checks to ensure that backups are not running.  If jobs are running, they will be canceled.  This action will **delete all backups** as part of the process.

#### How It Works
- The play starts by reading all environments from the Ansible Inventory and cancels any corresponding Protection Jobs if active.
- Upon completion of the job stop, the job is deleted, **including all backups**.
- After the job is successfully removed, each Source is registered as a new Protection Job, with the corresponding endpoint as the name of that Protection Job.

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this playbook, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | var_validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |

## Ansible Inventory Configuration
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

To fully leverage this Ansible Play, you must configure your Ansible Inventory file with certain keys and values. This makes it much easier to manage the overall experience. See [Configure Your Ansible Inventory](../configuring-your-ansible-inventory.md).

This is an example inventory file: (Remember to change it to suit your environment.)
```ini
[linux]
10.2.46.96
10.2.46.97
10.2.46.98
10.2.46.99

[linux:vars]
ansible_user=root

[windows]
10.2.45.88
10.2.45.89

[windows:vars]
ansible_user=administrator
ansible_password=secret
ansible_connection=winrm
ansible_winrm_server_cert_validation=ignore

# => Group all Physical Servers.  This grouping is used by the Demos and Complete
# => Examples to identify Physical Servers
[physical:children]
linux
windows

# => Declare the VMware environments to manage.
[vmware]
vcenter01 ansible_host=10.2.x.x

[vmware:vars]
type=VMware
vmware_type=VCenter
source_username=administrator
source_password=password

# => Declare the GenericNas endpoints to manage
[generic_nas]
export_path endpoint="10.2.x.x:/export_path" nas_protocol=NFS
nas_share endpoint="\\\\10.2.x.x\\nas_share"
data endpoint="\\\\10.2.x.x\\data"

# => Default variables for GenericNas endpoints.
[generic_nas:vars]
type=GenericNas
nas_protocol=SMB
nas_username=.\cohesity
nas_password=password
```

## Customize Your Playbooks
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

The combined source file for these two playbooks is located at the root of the role in `examples/demos/jobs.yml`.

### Register Protection Jobs for all hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that registers an existing Protection Source as a new Protection Job for all hosts in the inventory. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

```yaml
# => Cohesity Protection Jobs for Physical, VMware, and GenericNAS environments
# =>
# => Role: cohesity.cohesity_ansible_role
# => Version: 0.5.0
# => Date: 2018-12-28
# =>

# => Create a new Protection Job by Endpoint based on Ansible Inventory
# =>
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
      - cohesity.cohesity_ansible_role
    tasks:
        # => Manage Physical
      - name: Create new Protection Jobs for each Physical Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: present
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              endpoint: "{{ hostvars[item]['ansible_host'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'sources', 'register', 'physical' ]

      - name: Start On-Demand Protection Job Execution for each Physical Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: started
              job_name: "{{ hostvars[item]['ansible_host'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'sources', 'started', 'physical' ]

        # => Manage VMware
      - name: Create new Protection Jobs for each VMware Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: present
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              endpoint: "{{ hostvars[item]['ansible_host'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

      - name: Start On-Demand Protection Job Execution for each VMware Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: started
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'sources', 'started', 'vmware' ]

        # => Manage Generic NAS Endpoints
      - name: Create new Protection Jobs for each NAS Endpoint
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: present
              job_name: "{{ hostvars[item]['endpoint'] }}"
              endpoint: "{{ hostvars[item]['endpoint'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'sources', 'register', 'generic_nas' ]

      - name: Start On-Demand Protection Job Execution for each NAS Endpoint
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: started
              job_name: "{{ hostvars[item]['endpoint'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'sources', 'started', 'generic_nas' ]

```

### Remove Protection Jobs for all hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that removes an existing Protection Job and deletes the backups for all hosts in the inventory. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

```yaml
# => Cohesity Protection Jobs for Physical, VMware, and GenericNAS environments
# =>
# => Role: cohesity.cohesity_ansible_role
# => Version: 0.5.0
# => Date: 2018-12-28
# =>

# => Remove Protection Jobs by Endpoint based on Ansible Inventory
# =>
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
      - cohesity.cohesity_ansible_role
    tasks:
        # => Manage Physical
      - name: Stop existing Protection Job Execution for each Physical Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: stopped
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              cancel_active: True
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'sources', 'stopped', 'remove', 'physical' ]

      - name: Remove Protection Jobs for each Physical Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: absent
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              endpoint: "{{ hostvars[item]['ansible_host'] }}"
              delete_backups: True
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'sources', 'remove', 'physical' ]

        # => Manage VMware
      - name: Stop existing Protection Job Execution for each VMware Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: stopped
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              environment: "{{ hostvars[item]['type'] }}"
              cancel_active: True
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'sources', 'stopped', 'remove', 'vmware' ]

      - name: Remove Protection Jobs for each VMware Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: absent
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              endpoint: "{{ hostvars[item]['ansible_host'] }}"
              environment: "{{ hostvars[item]['type'] }}"
              delete_backups: True
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'sources', 'remove', 'vmware' ]

        # => Manage Generic NAS Endpoints
      - name: Stop existing Protection Job Execution for each NAS Endpoint
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: stopped
              job_name: "{{ hostvars[item]['endpoint'] }}"
              environment: "{{ hostvars[item]['type'] }}"
              cancel_active: True
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'sources', 'stopped', 'remove', 'generic_nas' ]

      - name: Remove Protection Jobs for each NAS Endpoint
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs }}"
          cohesity_protection:
              state: absent
              job_name: "{{ hostvars[item]['endpoint'] }}"
              endpoint: "{{ hostvars[item]['endpoint'] }}"
              environment: "{{ hostvars[item]['type'] }}"
              delete_backups: True
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'sources', 'remove', 'generic_nas' ]

```

