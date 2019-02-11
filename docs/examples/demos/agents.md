# Install and Remove the Cohesity Agent Using Ansible Inventory

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Create a Custom Installation Playbook for Linux Hosts](#Create-a-custom-installation-playbook-for-Linux-hosts)
  - [Create a Custom Installation Playbook for Windows Hosts](#Create-a-custom-installation-playbook-for-Windows-hosts)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)

## Synopsis
[top](#Install-and-Remove-the-Cohesity-Agent-Using-Ansible-Inventory)

This example play employs the Ansible Inventory to dynamically remove and install the Cohesity Agent on the supported platforms. The source file for this playbook is located at the root of the role in `examples/demos/agents.yml`.
> **IMPORTANT**!<br>
  This example play should be considered for demo purposes only.  This play uninstalls and then installs the Cohesity Agent on all Physical hosts based on the Ansible Inventory.  There are no job or source validations nor state checks to ensure that backups are not running.

#### How It Works
- The play starts by reading all `linux` servers from the Ansible Inventory and uninstalling the agent (if present).
- Upon completion of agent removal, the latest version of the agent is installed on the `linux` servers.
- The next step is to perform the uninstallation of the Agent on `windows` servers.
  - This is followed by a mandatory reboot of the server as a part of the uninstallation (only if the agent was present).
- Once the reboot is complete, the latest version of the agent is installed on the `windows` servers.
  - If the windows `install_type` is `volcbt`, then a reboot of the windows servers is triggered.

> **Notes:**
  - Currently, the Cohesity Ansible Role requires Cohesity Cluster Administrator access.
  - Before using this playbook, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Install-and-Remove-the-Cohesity-Agent-Using-Ansible-Inventory)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | var_validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |

## Ansible Inventory Configuration
[top](#Install-and-Remove-the-Cohesity-Agent-Using-Ansible-Inventory)

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
```

## Customize Your Playbooks
[top](#Install-and-Remove-the-Cohesity-Agent-Using-Ansible-Inventory)

The combined source file for these two playbooks is located at the root of the role in `examples/demos/agents.yml`.

### Create a Custom Installation Playbook for Linux Hosts
[top](#Install-and-Remove-the-Cohesity-Agent-Using-Ansible-Inventory)

Here is an example playbook that installs the Cohesity agent on all `linux` hosts. (Remember to change it to suit your environment.)
> **Notes:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.
  - When using the default download location, the Cohesity agent installer is placed in `/tmp/<temp-dir>`.  If your environment prevents the use of `/tmp` with a `noexec` option, then you must set an alternate download location.

```yaml
# => Cohesity Agent Management
# =>
# => Role: cohesity.cohesity_ansible_role
# =>

# => Install the Cohesity Agent on each Linux host
# => specified in the Ansible inventory
# =>
---
  - hosts: linux
    # => We need to specify these variables to connect
    # => to the Cohesity cluster
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
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Install new Cohesity Agent on each Linux Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
```



### Create a Custom Installation Playbook for Windows Hosts
[top](#Install-and-Remove-the-Cohesity-Agent-Using-Ansible-Inventory)

Here is an example playbook that installs the Cohesity agent on all `windows` hosts. (Remember to change it to suit your environment.)
> **Notes:**
  - Before using these example playbooks, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.
  - Cohesity Agent installation on Windows supports two types of Agent install types: `filecbt` and `volcbt`.  When installing or removing the agent and selecting a `volcbt` type, you must reboot the Windows server to complete the action.

```yaml
# => Install the Cohesity Agent on each Windows host
# => specified in the Ansible inventory
# =>
  - hosts: windows
    # => We need to specify these variables to connect
    # => to the Cohesity cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
        var_agent_install_type: volcbt
        var_windows_reboot: True
    gather_facts: no
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Remove Cohesity Agent from each Windows Server
        include_role:
            name: cohesity.cohesity_ansible_role
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
            name: cohesity.cohesity_ansible_role
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

## Ansible Inventory Configuration
[top](#Install-and-Remove-the-Cohesity-Agent-Using-Ansible-Inventory)

To fully leverage this Ansible Play, you must configure your Ansible Inventory file with certain keys and values. This makes it much easier to manage the overall experience. See [Configure Your Ansible Inventory](../configuring-your-ansible-inventory.md).

Here is an example Inventory File. Before using it, edit it to address your own environment.
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
