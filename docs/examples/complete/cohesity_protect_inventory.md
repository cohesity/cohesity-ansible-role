# Deploy Full Cohesity Protection Using Ansible Inventory

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Working with the Cohesity Facts Module](#Working-with-the-cohesity_facts-Module)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Register all hosts in the Inventory to enable full protection on the selected Cohesity cluster](#Register-All-hosts-in-the-inventory-to-enable-Full-Protection-on-the-selected-Cohesity-Cluster)

## Synopsis
[top](#Deploy-Full-Cohesity-Protection-Using-Ansible-Inventory)

This example play can help accelerate the usage of the Cohesity Ansible integration by automatically generating a full-stack deployment of Cohesity Agents, Sources, and Jobs.  The source file for this playbook is located at the root of the role in `examples/complete/cohesity_protect_inventory.yml`.

#### How It Works
- The play starts by reading all Physical servers from the Ansible Inventory and installing the agent.
- Upon completion of the agent installation, each Protection Source is registered based on environment type:
  - Physical
  - VMware
  - GenericNAS
- The final step is to create Protection Jobs for Linux Servers, Windows Servers, VMware and GenericNAS
- Once all the Protection Jobs are created, an immediate, one-time execution is started.

### Requirements
[top](#Deploy-Full-Cohesity-Protection-Using-Ansible-Inventory)

  - A physical or virtual Cohesity system. The modules were developed with Cohesity DataPlatform version 6.1.0
  - Ansible 2.6
  - Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this playbook, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Deploy-Full-Cohesity-Protection-Using-Ansible-Inventory)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | var_validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |

## Ansible Inventory Configuration
[top](#Deploy-Full-Cohesity-Protection-Using-Ansible-Inventory)

To fully leverage this Ansible Play, you must configure your Ansible Inventory file with certain keys and values. This makes it much easier to manage the overall experience. See [Configure Your Ansible Inventory](../configuring-your-ansible-inventory.md).

Here is an example inventory file: (Remember to change it to suit your environment.)
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
install_type=volcbt
reboot_after_install=True
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
## Working with the cohesity_facts Module
[top](#Deploy-Full-Cohesity-Protection-Using-Ansible-Inventory)

This play leverages certain data collected as part of the `cohesity_facts` module distributed with the Cohesity Ansible Role.  For more information, see [Cohesity Facts](../../modules/cohesity_facts.md).

## Customize Your Playbooks
[top](#Deploy-Full-Cohesity-Protection-Using-Ansible-Inventory)

### Register all hosts in the Inventory to enable full protection on the selected Cohesity cluster

Here is an example playbook that queries the inventory to install Agents on all Linux and Windows hosts, register each host as a Protection Source, and then create and start a protection job for Linux, Windows, VMware, GenericNAS hosts. The source file for this playbook is located at the root of the role in `examples/complete/cohesity_protect_inventory.yml`.  (Remember to change it to suit your environment.)

```yaml
# => Cohesity Full Protection for Physical, VMware, and GenericNAS environments
# =>
# => Role: cohesity.cohesity_ansible_role
# => Version: 0.6.0
# => Date: 2018-12-28
# =>

# => Install the Cohesity Agent on each identified Linux and Windows environment
# =>
---
  - hosts: linux
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    become: true
    # => We need to gather facts to determine the OS type of
    # => the machine
    gather_facts: yes
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_agent:
                state: present
        tags: [ 'cohesity', 'agent', 'install', 'physical', 'linux' ]

  - hosts: windows
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
      - name: Install new Cohesity Agent on each Windows Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: win_agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_agent:
                state: present
                install_type: "{{ hostvars['install_type'] }}"
                reboot: "{{ hostvars['reboot_after_install'] }}"
        tags: [ 'cohesity', 'agent', 'install', 'physical', 'windows' ]


# => Register each host as a new Cohesity Protection Source
# =>

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
      - name: Create new Protection Source for each Linux Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_source:
                state: present
                endpoint: "{{ item }}"
                host_type: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups['linux'] }}"
        tags: [ 'cohesity', 'sources', 'register', 'physical' ]
    
      - name: Create new Protection Source for each windows Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_source:
                state: present
                endpoint: "{{ item }}"
                host_type: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups['windows'] }}"
        tags: [ 'cohesity', 'sources', 'register', 'physical' ]

      - name: Create new Protection Source for each Vmware Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_source:
                state: present
                endpoint: "{{ item }}"
                environment: "{{ hostvars[item]['type'] }}"
                vmware_type: "{{ hostvars[item]['vmware_type'] }}"
                source_username: "{{ hostvars[item]['source_username'] }}"
                source_password: "{{ hostvars[item]['source_password'] }}"
        with_items: "{{ groups['vmware'] }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

      - name: Create new Protection Source for each NAS Endpoint
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_source:
                state: present
                endpoint: "{{ hostvars[item]['endpoint'] }}"
                environment: "{{ hostvars[item]['type'] }}"
                nas_protocol: "{{ hostvars[item]['nas_protocol'] | default('') }}"
                nas_username: "{{ hostvars[item]['nas_username'] | default('') }}"
                nas_password: "{{ hostvars[item]['nas_password'] | default('') }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'sources', 'register', 'generic_nas' ]


# => Create a new Protection Job for Linux, Windows, VMware, GenericNAS hosts
# =>
        # => Manage Physical
      - name: Create new Protection Job with all Linux Physical Servers
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: present
              job_name: protect_physical_linux
              sources:
                - endpoint: "{{ item }}"
        with_items: "{{ groups['linux'] }}"
        tags: [ 'cohesity', 'jobs', 'create', 'physical' ]
      
      - name: Create new Protection Job with all Windows Physical Servers
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: present
              job_name: protect_physical_windows
              sources:
                - endpoint: "{{ item }}"
        with_items: "{{ groups['windows'] }}"
        tags: [ 'cohesity', 'jobs', 'create', 'physical' ]

      - name: Create new Protection Jobs for each VMware Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: present
              job_name: "{{ item }}"
              sources:
                - endpoint: "{{ item }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups['vmware'] }}"
        tags: [ 'cohesity', 'jobs', 'create', 'vmware' ]

      - name: Create new Protection Jobs for each NAS Endpoint
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: present
              job_name: "{{ hostvars[item]['endpoint'] }}"
              sources:
                - endpoint: "{{ hostvars[item]['endpoint'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'jobs', 'create', 'generic_nas' ]

        # => Start Protection for each identified Cohesity Protection Job
        # =>
      - name: Start On-Demand Protection Job Execution for Linux Physical Servers
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: started
              job_name: protect_physical_linux
        tags: [ 'cohesity', 'jobs', 'started', 'physical' ]
      
      - name: Start On-Demand Protection Job Execution for Windows Physical Servers
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: started
              job_name: protect_physical_windows
        tags: [ 'cohesity', 'jobs', 'started', 'physical' ]

      - name: Start On-Demand Protection Job Execution for each VMware Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: started
              job_name: "{{ item }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups['vmware'] }}"
        tags: [ 'cohesity', 'jobs', 'started', 'vmware' ]


      - name: Start On-Demand Protection Job Execution for each NAS Endpoint
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: started
              job_name: "{{ hostvars[item]['endpoint'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'jobs', 'started', 'generic_nas' ]

```