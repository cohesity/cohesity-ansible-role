# Remove and Register Cohesity Sources Using Ansible Inventory

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Register Protection Sources for all hosts in the inventory](#Register-Protection-Sources-for-all-hosts-in-the-inventory)
  - [Unregister Protection Sources for all hosts in the inventory](#Unregister-Protection-Sources-for-all-hosts-in-the-inventory)

## Synopsis
[top](#Remove-and-Register-Cohesity-Sources-Using-Ansible-Inventory)

This example play leverages the Ansible Inventory to dynamically remove and register Protection Sources for supported Environment Types.  The source file for this playbook is located at the root of the role in `examples/demos/sources.yml`.
> **IMPORTANT**!<br>
  This example play should be considered for demo purposes only. This play removes and then registers all Physical, VMware, and GenericNAS Protection Sources based on the Ansible Inventory.  There are no job validations or state checks to ensure that backups are not running.  If jobs exist for the Source, an error is raised and the play fails.

#### How It Works
- The play starts by reading all environments from the Ansible Inventory and removing the corresponding Source(s).
- Upon completion of the removal, the endpoint is registered as a new Protection Source.

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this playbook, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Remove-and-Register-Cohesity-Sources-Using-Ansible-Inventory)


| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | var_validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |

## Ansible Inventory Configuration
[top](#Remove-and-Register-Cohesity-Sources-Using-Ansible-Inventory)

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
[top](#Remove-and-Register-Cohesity-Sources-Using-Ansible-Inventory)

The combined source file for these two playbooks is located at the root of the role in `examples/demos/sources.yml`.

### Register Protection Sources for all hosts in the inventory
[top](#Remove-and-Register-Cohesity-Sources-Using-Ansible-Inventory)

Here is an example playbook that registers a new Protection Source for all hosts in the inventory. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

```yaml
# => Cohesity Protection Sources for Physical, VMware, and GenericNAS environments
# =>
# => Role: cohesity.ansible
# => Version: 0.6.0
# => Date: 2018-12-28
# =>

# => Register each Protection Source by Environment based on Ansible Inventory
# =>
---
  - hosts: workstation
    # => We need to specify these variables to connect
    # => to the Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.ansible
    tasks:
      # => Cycle through each member of the Ansible Group [physical] and register as a Cohesity Protection Source
      - name: Create new Protection Source for each Physical Server
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
                host_type: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'sources', 'register', 'physical' ]

      # => Cycle through each member of the Ansible Group [vmware] and register as a Cohesity Protection Source
      - name: Create new Protection Source for each Vmware Server
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
                environment: "{{ hostvars[item]['type'] }}"
                vmware_type: "{{ hostvars[item]['vmware_type'] }}"
                source_username: "{{ hostvars[item]['source_username'] }}"
                source_password: "{{ hostvars[item]['source_password'] }}"
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

      # => Cycle through each member of the Ansible Group [generic_nas] and register as a Cohesity Protection Source
      - name: Create new Protection Source for each NAS Endpoint
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
                endpoint: "{{ hostvars[item]['endpoint'] }}"
                environment: "{{ hostvars[item]['type'] }}"
                nas_protocol: "{{ hostvars[item]['nas_protocol'] | default('') }}"
                nas_username: "{{ hostvars[item]['nas_username'] | default('') }}"
                nas_password: "{{ hostvars[item]['nas_password'] | default('') }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'sources', 'register', 'generic_nas' ]
```

### Unregister Protection Sources for all hosts in the inventory
[top](#Remove-and-Register-Cohesity-Sources-Using-Ansible-Inventory)

Here is an example playbook that unregisters all Protection Sources for the hosts in the inventory. (Remember to change it to suit your environment.)
> **Notes:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.
  - The removal of a Protection Source with an existing Protection Job is unsupported at this time.

```yaml
# => Cohesity Protection Sources for Physical, VMware, and GenericNAS environments
# =>
# => Role: cohesity.ansible
# => Version: 0.6.0
# => Date: 2018-12-28
# =>

# => Register each Protection Source by Environment based on Ansible Inventory
# =>
---
  - hosts: workstation
    # => We need to specify these variables to connect
    # => to the Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    gather_facts: no
    roles:
      - cohesity.ansible
    tasks:
      # => Cycle through each member of the Ansible Group [physical] and remove the Cohesity Protection Source
      - name: Remove registered Protection Source for each Physical Server
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: absent
                endpoint: "{{ hostvars[item]['ansible_host'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'sources', 'register', 'physical' ]

      # => Cycle through each member of the Ansible Group [vmware] and remove the Cohesity Protection Source
      - name: Remove registered Protection Source for each Vmware Server
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: absent
                endpoint: "{{ hostvars[item]['ansible_host'] }}"
                environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.vmware }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]

      # => Cycle through each member of the Ansible Group [generic_nas] and remove the Cohesity Protection Source
      - name: Remove registered Protection Source for each NAS Endpoint
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: absent
                endpoint: "{{ hostvars[item]['endpoint'] }}"
                environment: "{{ hostvars[item]['type'] }}"
        with_items: "{{ groups.generic_nas }}"
        tags: [ 'cohesity', 'sources', 'register', 'generic_nas' ]
```
