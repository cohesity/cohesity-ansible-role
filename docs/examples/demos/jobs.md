# Create and Manage Cohesity Jobs Using Ansible Inventory

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Customize Your Playbooks](#Customize-Your-Playbooks)
  - [Register Protection Job for all Linux hosts in the inventory](#Register-Protection-Job-for-all-Linux-hosts-in-the-inventory)
  - [Register protection Job for all Windows hosts in the inventory](#Register-protection-Job-for-all-Windows-hosts-in-the-inventory)
  - [Register protection Jobs for all VMware hosts in the inventory](#Register-protection-Jobs-for-all-VMware-hosts-in-the-inventory)
  - [Register a VMware protection job for a set of VMs](#Register-a-VMware-protection-job-for-a-set-of-VMs)
  - [Register a VMware protection job with VM exclusions](#Register-a-VMware-protection-job-with-VM-exclusions)
  - [Update a VMware protection job exlcuding a set of VMs](#Update-a-VMware-protection-job-exlcuding-a-set-of-VMs)
  - [Update a VMware protection job to protect a set of VMs](#Update-a-VMware-protection-job-to-protect-a-set-of-VMs)
  - [Register protection Jobs for all GenericNAS hosts in the inventory](#Register-protection-Jobs-for-all-GenericNAS-hosts-in-the-inventory)
  - [Remove Protection Job for all Linux hosts in the inventory](#Remove-Protection-Job-for-all-Linux-hosts-in-the-inventory)
  - [Remove Protection Job for all Windows hosts in the inventory](#Remove-Protection-Job-for-all-Windows-hosts-in-the-inventory)
  - [Remove Protection Jobs for all VMware hosts in the inventory](#Remove-Protection-Jobs-for-all-VMware-hosts-in-the-inventory)
  - [Remove Protection Jobs for all GenericNAS hosts in the inventory](#Remove-Protection-Jobs-for-all-GenericNAS-hosts-in-the-inventory)
## Synopsis
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

This example play leverages the Ansible Inventory to dynamically remove and create Protection Jobs for existing Protection Sources.  The source file for this playbook is located at the root of the role in `examples/demos/jobs.yml`.
> **IMPORTANT**!<br>
  This example play should be considered for demo purposes only.  This play removes and then registers all Physical, VMware, and GenericNAS Protection Jobs based on the Ansible Inventory.  There are no job validations or state checks to ensure that backups are not running.  If jobs are running, they will be canceled.  This action will **delete all backups** as part of the process.

#### How It Works
- The play starts by reading all environments from the Ansible Inventory and cancels any corresponding Protection Jobs if active.
- Upon completion of the job stop, the job is deleted, **including all backups**.
- After the job is successfully removed, Protection job is created with sources

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
[workstation]
127.0.0.1 ansible_connection=local

[linux]
10.2.46.96
10.2.46.97
10.2.46.98
10.2.46.99

[linux:vars]
type=Linux
ansible_user=root

[windows]
10.2.45.88
10.2.45.89

[windows:vars]
type=Windows
ansible_user=administrator
ansible_password=secret
ansible_connection=winrm
ansible_winrm_server_cert_validation=ignore


# => Declare the VMware environments to manage.
[vmware]
10.2.x.x

[vmware:vars]
type=VMware
vmware_type=VCenter
source_username=administrator
source_password=password

[include_vms]
cohesity-centos1
cohesity-centos2

[exclude_vms]
cohesity-ubuntu1
cohesity-ubuntu2

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

### Register Protection Job for all linux hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that registers a new Protection Job for all Linux hosts in the inventory and starts the protection job run. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_linux.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_linux.yml -e "username=admin password=admin"
  ```

```yaml
# => Create a new Protection Job for Linux hosts in inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
        # => Manage Physical Linux hosts
      - name: Create new Protection Job for Physical linux Servers
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
              job_name: "protect_physical_linux"
              sources: 
                 - endpoint : "{{ item }}"
                   paths:
                    - includeFilePath: "/"
                      excludeFilePaths:
                        - "/home"
                        - "/opt"
                      skipNestedVolumes: False
        with_items: "{{ groups['linux'] }}"
      
      - name: Start On-Demand Protection Job Execution for Physical linux Servers
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
              job_name: "protect_physical_linux"
```

### Register Protection Job for all Windows hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that registers a new Protection Job for all Windows hosts in the inventory and starts the protection job run. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_windows.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_windows.yml -e "username=admin password=admin"
  ```

```yaml
# => Create a new Protection Job for Windows hosts in inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
        # => Manage Physical Windows hosts
      - name: Create new Protection Job for Physical windows Servers
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
              job_name: "protect_physical_windows"
              sources: 
                 - endpoint : "{{ item }}"
                   paths:
                    - includeFilePath: "C:\\"
                      excludeFilePaths:
                        - "C:\\Program Files"
                      skipNestedVolumes: False
        with_items: "{{ groups['windows'] }}"

      - name: Start On-Demand Protection Job Execution for Physical windows Servers
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
              job_name: "protect_physical_windows"
```

### Register Protection Jobs for all VMware hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that registers new Protection Jobs for all VMware hosts in the inventory and starts the protection job run. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_vmware.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_VMware.yml -e "username=admin password=admin"
  ```

```yaml
# => Create a new Protection Jobs for all VMware hosts in inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
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
              job_name: "{{ item }}"
              sources:
                - endpoint: "{{ item }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups['vmware'] }}"
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
              job_name: "{{ item }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups['vmware'] }}"
        tags: [ 'cohesity', 'sources', 'started', 'vmware' ]
```

### Register a VMware protection job for a set of VMs
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that registers a new Protection Job for a set of VMs and starts the protection job run. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_include_vms.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_include_vms.yml -e "username=admin password=admin"
  ```

```yaml
# => Create a new Protection Job for a set of VMs given in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      # => Manage VMware
      - name: Create new Protection Job
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
              job_name: "protect_vms"
              sources:
                - endpoint: "vcenter_ip_or_hostname"
              environment: "VMware"
              include_vms: "{{ groups['include_vms'] }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

      - name: Start On-Demand Protection Job Execution
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
              job_name: "protect_vms"
              environment: "VMware"
        tags: [ 'cohesity', 'sources', 'started', 'vmware' ]
```

### Register a VMware protection job with VM exclusions
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that registers a new VMware Protection Job excluding a set of VMs and starts the protection job run. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_exclude_vms.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_exclude_vms.yml -e "username=admin password=admin"
  ```

```yaml
# => Create a new VMware Protection Job exclusing a set of VMs given in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      # => Manage VMware
      - name: Create new Protection Job
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
              job_name: "protect_vcenter1"
              sources:
                - endpoint: "vcenter_ip_or_hostname"
              environment: "VMware"
              exclude_vms: "{{ groups['exclude_vms'] }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

      - name: Start On-Demand Protection Job Execution
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
              job_name: "protect_vcenter1"
              environment: "VMware"
        tags: [ 'cohesity', 'sources', 'started', 'vmware' ]
```

### Update a VMware protection job exlcuding a set of VMs
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that updates an existing VMware Protection Job excluding a set of VMs. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_exclude_vms.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_exclude_vms.yml -e "username=admin password=admin"
  ```

```yaml
# => Update an existing Protection Job excluding a set of VMs given in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      # => Manage VMware
      - name: Update Protection Job
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
              job_name: "protect_vms"
              environment: "VMware"
              exclude_vms: "{{ groups['exclude_vms'] }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

```

### Update a VMware protection job to protect a set of VMs
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that updates an existing VMware Protection Job to protect a set of VMs. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_include_vms.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_include_vms.yml -e "username=admin password=admin"
  ```

```yaml
# => Update an existing Protection Job to protect a set of VMs given in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      # => Manage VMware
      - name: Update Protection Job
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
              job_name: "protect_vms"
              environment: "VMware"
              include_vms: "{{ groups['include_vms'] }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

```

### Register Protection Jobs for all GenericNAS hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that registers new Protection Jobs for all GenericNAS hosts in the inventory and starts the protection job run. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `protection_job_GenericNAS.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_jobs_GenericNAS.yml -e "username=admin password=admin"
  ```

```yaml
# => Create a new Protection Jobs for all GenericNAS hosts in inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
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
              sources: 
                 - endpoint: "{{ hostvars[item]['endpoint'] }}"
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

### Remove Protection Job for all Linux hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that stops the protection job run, removes the existing Protection Job and deletes the backups for all Linux hosts in the inventory. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `remove_protection_jobs_linux.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> remove_protection_jobs_linux.yml -e "username=admin password=admin"
  ```

```yaml
# => Remove Protection Job for all Linux hosts in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
        # => Manage Physical Linux hosts
      - name: Stop existing Protection Job Execution for Physical linux Servers
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
              job_name: "protect_physical_linux"
              cancel_active: True

      - name: Remove Protection Job for Physical linux server
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
              job_name: "protect_physical_linux"
              delete_backups: True
```

### Remove Protection Job for all Windows hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that stops the protection job run, removes the existing Protection Job and deletes the backups for all Windows hosts in the inventory. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `remove_protection_jobs_windows.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> remove_protection_jobs_windows.yml -e "username=admin password=admin"
  ```

```yaml
# => Remove Protection Job for all Windows hosts in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
        # => Manage Physical Windows hosts
      - name: Stop existing Protection Job Execution for Physical windows Servers
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
              job_name: "protect_physical_windows"
              cancel_active: True

      - name: Remove Protection Job for Physical windows server
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
              job_name: "protect_physical_windows"
              delete_backups: True
```

### Remove Protection Jobs for all VMware hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that stops the protection job run, removes the existing Protection Jobs and deletes the backups for all VMware hosts in the inventory. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `remove_protection_jobs_VMware.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> remove_protection_jobs_VMware.yml -e "username=admin password=admin"
  ```

```yaml
# => Remove Protection Jobs for all VMware hosts in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
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
              job_name: "{{ item }}"
              environment: "{{ hostvars[item]['type'] }}"
              cancel_active: True
        with_items: "{{ groups['vmware'] }}"
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
              job_name: "{{ item }}"
              endpoint: "{{ item }}"
              environment: "{{ hostvars[item]['type'] }}"
              delete_backups: True
        with_items: "{{ groups['vmware'] }}"
        tags: [ 'cohesity', 'sources', 'remove', 'vmware' ]
```

### Remove Protection Jobs for all GenericNAS hosts in the inventory
[top](#Create-and-Manage-Cohesity-Jobs-Using-Ansible-Inventory)

Here is an example playbook that stops the protection job run, removes the existing Protection Jobs and deletes the backups for all GenericNAS hosts in the inventory. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

You can create a file called `remove_protection_jobs_GenericNAS.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> remove_protection_jobs_GenericNAS.yml -e "username=admin password=admin"
  ```

```yaml
# => Remove Protection Jobs for all GenericNAS hosts in the inventory
# =>
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
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



