# Cohesity Full Protection using Ansible Inventory

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Working with Cohesity Facts module](#Working-with-Cohesity-Facts-module)
- [Customizing your playbooks](#Customizing-your-playbooks)
  - [Register All hosts in the inventory to enable Full Protection on the selected Cohesity Cluster](#Register-All-hosts-in-the-inventory-to-enable-Full-Protection-on-the-selected-Cohesity-Cluster)

## SYNOPSIS
[top](#Cohesity-Full-Protection-using-Ansible-Inventory)

This example play can help to accelerate the usage of the Cohesity Ansible integration by generating a full stack deployment of Cohesity Agents, Sources, and Jobs automatically.  This source file for this playbook is located at the root of the role in `examples/complete/cohesity_protect_inventory.yml`

#### How it works 
- The play will start by reading all Physical servers from the Ansible Inventory and installing the agent.
- Upon completion of the agent installation, each Protection Source will be registered based on environment type:
  - Physical
  - VMware
  - GenericNas
- The final step will be to create a new Protection job for each of the Protection Sources.
- Once all jobs are created, an immediate, one-time execution will be started.

### Requirements
[top](#Cohesity-Full-Protection-using-Ansible-Inventory)

  - A physical or virtual Cohesity system. The modules were developed with Cohesity version 6.1.0
  - Ansible 2.6
  - Python >= 2.6

> **Notes**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using this playbook, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Cohesity-Full-Protection-using-Ansible-Inventory)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity Cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | var_validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |

## Ansible Inventory Configuration
[top](#Cohesity-Full-Protection-using-Ansible-Inventory)

To fully leverage this Ansible Play, you must configure your Ansible Inventory file with certain keys and values. This allows for a much easier management of the overall experience.

For more information [see our Guide on Configuring your Ansible Inventory](examples/configuring-your-ansible-inventory.md)

Here is an example inventory file. Please change it as per your environment.
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

## Customizing your playbooks
[top](#Cohesity-Full-Protection-using-Ansible-Inventory)

### Register All hosts in the inventory to enable Full Protection on the selected Cohesity Cluster

Here is an example playbook that queries the inventory to install Agents on all hosts in the Physical Group, Register each Environment type member as a Protection Source, then create and start a Protection Job for each host. The source file for this playbook is located at the root of the role in `examples/complete/cohesity_protect_inventory.yml`.  Please change it as per your environment.

```yaml
# => Cohesity Full Protection for Physical, VMware, and GenericNAS environments
# =>
# => Role: cohesity.ansible
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
        - cohesity.ansible
    tasks:
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.ansible
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
        - cohesity.ansible
    tasks:
      - name: Install new Cohesity Agent on each Windows Physical Server
        include_role:
            name: cohesity.ansible
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


# => Register each environment as a new Cohesity Protection Source
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
      - cohesity.ansible
    tasks:
      - name: Create new Protection Source for each Physical Server
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_source:
                state: present
                endpoint: "{{ hostvars[item]['ansible_host'] }}"
                host_type: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'sources', 'register', 'physical' ]

      - name: Create new Protection Source for each Vmware Server
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
            cohesity_source:
                state: present
                endpoint: "{{ hostvars[item]['ansible_host'] }}"
                environment: "{{ hostvars[item]['type'] }}"
                vmware_type: "{{ hostvars[item]['vmware_type'] }}"
                source_username: "{{ hostvars[item]['source_username'] }}"
                source_password: "{{ hostvars[item]['source_password'] }}"
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

      - name: Create new Protection Source for each NAS Endpoint
        include_role:
            name: cohesity.ansible
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


# => Create a new Protection Job for each identified Cohesity Protection Source
# =>
        # => Manage Physical
      - name: Create new Protection Jobs for each Physical Server
        include_role:
          name: cohesity.ansible
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: present
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              endpoint: "{{ hostvars[item]['ansible_host'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'jobs', 'create', 'physical' ]

      - name: Create new Protection Jobs for each VMware Server
        include_role:
          name: cohesity.ansible
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: present
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              endpoint: "{{ hostvars[item]['ansible_host'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'jobs', 'create', 'vmware' ]

      - name: Create new Protection Jobs for each NAS Endpoint
        include_role:
          name: cohesity.ansible
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: present
              job_name: "{{ hostvars[item]['endpoint'] }}"
              endpoint: "{{ hostvars[item]['endpoint'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'jobs', 'create', 'generic_nas' ]

        # => Start Protection for each identified Cohesity Protection Job
        # =>
      - name: Start On-Demand Protection Job Execution for each Physical Server
        include_role:
          name: cohesity.ansible
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: started
              job_name: "{{ hostvars[item]['ansible_host'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'jobs', 'started', 'physical' ]

      - name: Start On-Demand Protection Job Execution for each VMware Server
        include_role:
          name: cohesity.ansible
          tasks_from: job
        vars:
          cohesity_server: "{{ var_cohesity_server }}"
          cohesity_admin: "{{ var_cohesity_admin }}"
          cohesity_password: "{{ var_cohesity_password }}"
          cohesity_validate_certs: "{{ var_validate_certs | default('True') }}"
          cohesity_protection:
              state: started
              job_name: "{{ hostvars[item]['ansible_host'] }}"
              environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'jobs', 'started', 'vmware' ]


      - name: Start On-Demand Protection Job Execution for each NAS Endpoint
        include_role:
          name: cohesity.ansible
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