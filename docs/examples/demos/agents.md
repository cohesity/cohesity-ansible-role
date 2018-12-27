# Cohesity Agent uninstallation and installation using Ansible Inventory

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Customizing your playbooks](#Customizing-your-playbooks)
  - [Creating a custom installation playbook for Linux hosts](#Creating-a-custom-installation-playbook-for-Linux-hosts)
  - [Creating a custom installation playbook for Windows hosts](#Creating-a-custom-installation-playbook-for-Windows-hosts)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)

## SYNOPSIS
[top](#cohesity-agent-uninstallation-and-installation-using-ansible-inventory)

This example play leverages the Ansible Inventory to dynamically remove and install the Cohesity Agent on the supported platforms.  This source file for this playbook is located at the root of the role in `examples/demos/agents.yml`
> **IMPORTANT**!<br>
  This example play should be considered for demo purposes only.  This will uninstall and then install the Cohesity Agent on all Physical hosts based on the Ansible Inventory.  There are no job or source validations nor state checks to ensure that backups are not running.

#### How it works
- The play starts by reading all `linux` servers from the Ansible Inventory and uninstalling the agent (if present).
- Upon completion of the agent removal, the latest version of the agent will be installed on the `linux` servers.
- The next step will be to perform the uninstallation of the Agent on `windows` servers.
  - This will be followed by a mandatory reboot of the server as a part of the uninstallation (only if the agent was present).
- Once the reboot is complete, the latest version of the agent will be installed on the `windows` servers.
  - If the windows `install_type` is `volcbt` then a reboot of the windows servers will be triggered.

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using this playbook, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#cohesity-agent-uninstallation-and-installation-using-ansible-inventory)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity Cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | var_validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |

## Ansible Inventory Configuration
[top](#cohesity-agent-uninstallation-and-installation-using-ansible-inventory)

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
```

## Customizing your playbooks
[top](#cohesity-agent-uninstallation-and-installation-using-ansible-inventory)

This combined source file for these two playbooks is located at the root of the role in `examples/demos/agents.yml`

### Creating a custom installation playbook for Linux hosts
[top](#cohesity-agent-uninstallation-and-installation-using-ansible-inventory)

Here is an example playbook that installs the Cohesity agent on all `linux` hosts. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.
  - When using the default download location, the Cohesity agent installer will be place in `/tmp/<temp-dir>` location.  If your environment prevents the use of `/tmp` with a `noexec` option, then the alternate location must be set.

```yaml
# => Cohesity Agent Management
# =>
# => Role: cohesity.ansible
# =>

# => Install the Cohesity Agent on each Linux host
# => specified in the Ansible inventory
# =>
---
  - hosts: linux
    # => We need to specify these variables to connect
    # => to the Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    # => We need to gather facts to determine the OS type of
    # => the machine
    gather_facts: yes
    become: true
    roles:
        - cohesity.ansible
    tasks:
      - name: Install new Cohesity Agent on each Linux Server
        include_role:
            name: cohesity.ansible
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
```



### Creating a custom installation playbook for Windows hosts
[top](#cohesity-agent-uninstallation-and-installation-using-ansible-inventory)

Here is an example playbook that installs the Cohesity agent on all `windows` hosts. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.
  - Cohesity Agent installation on Windows supports two types of Agent install types: `filecbt` and `volcbt`.  When installing or removing the agent and selecting a `volcbt` type, a reboot of the Windows server must be performed to complete the action.

```yaml
# => Install the Cohesity Agent on each Windows host
# => specified in the Ansible inventory
# =>
  - hosts: windows
    # => We need to specify these variables to connect
    # => to the Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
        var_agent_install_type: volcbt
        var_windows_reboot: True
    gather_facts: no
    roles:
        - cohesity.ansible
    tasks:
      - name: Remove Cohesity Agent from each Windows Server
        include_role:
            name: cohesity.ansible
            tasks_from: win_agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: absent
                reboot: "{{ var_windows_reboot }}"

      - name: Install new Cohesity Agent on each Windows Server
        include_role:
            name: cohesity.ansible
            tasks_from: win_agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
                install_type: "{{ var_agent_install_type }}"
                reboot: "{{ var_windows_reboot }}"
```
