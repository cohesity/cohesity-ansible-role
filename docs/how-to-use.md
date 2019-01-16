# How to Use
## Table of Contents
- [Getting Started](#Getting-Started)
- [Ansible Inventory](#Ansible-Inventory)
- [Using the Cohesity Ansible Role](#Using-the-cohesity-ansible-Role) 

## Getting Started
[top](#how-to-use)

If you haven't used Ansible before, watch this [quick-start video](https://www.ansible.com/resources/videos/quick-start-video) to get started.

## Ansible Inventory
[top](#how-to-use)

Make sure that your [Ansible Inventory File](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) is set up correctly.

  > **Tip:** What is the [Ansible Inventory File](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)?
  - Ansible works against multiple systems in your infrastructure at the same time. It does this by selecting a set of systems listed in Ansible’s inventory (default location: `/etc/ansible/hosts`).
  - You can also specify a different inventory file using the `-i <inventory_file>` option on the command line.
  - Aternately, you can include the inventory keypair in your ansible.cfg file to set the default file location
  ```ini
  >$> vi ansible.cfg
  [defaults]
  inventory = ./dev
  roles_path = ./roles
  ```
  - You can test if the inventory file is setup correctly by testing connection to all the hosts:
    - `ansible -m ping -i <inventory_file> all`
    - `ansible -m ping all` (if using the ansible.cfg overide)

  * This is an example of the inventory file. This inventory is simple and has only one host group called `linux`, but typically, the inventory file will contain multiple host groups.
    ```ini
      [linux]
      10.2.46.95
      10.2.46.96
      10.2.46.97

      [linux:vars]
      ansible_user=root
    ```

  * Here is a more advanced example of the inventory file. This inventory is contains multiple host groups (ubuntu and centos) and one roll-up group called `linux`. This model allows for creating different configurations and settings depending on the host information.  In this case, we can perform actions on only the `centos` or `ubuntu` groups or on both groups simultaneously by referencing the `linux` group
    ```ini
      [workstation]
      control ansible_connection=local ansible_host=10.2.46.94 type=Linux

      [linux]
      ubuntu
      centos

      [ubuntu]
      10.2.46.95

      [centos]
      10.2.46.96
      10.2.46.97

      [linux:vars]
      type=Linux

      [ubuntu:vars]
      ansible_user=ubuntu

      [centos:vars]
      ansible_user=root
      ansible_become=False

    ```

  * If you plan to run Ansible tasks against Windows hosts, please make sure that the [windows hosts are setup correctly](https://www.ansible.com/blog/connecting-to-a-windows-host).

  * For more information on how to use the Ansible Inventory, see [Configure Your Ansible Inventory](examples/configuring-your-ansible-inventory.md).

## Using the Cohesity Ansible Role
[top](#how-to-use)

* After [installing the Cohesity Ansible Role](setup.md), you can include the `cohesity.ansible` role and specific tasks along with the supported variables, in your plays.

* Below is an example playbook that uninstalls the Cohesity agent (if present), then installs the latest Cohesity agent on all the `linux` hosts in the inventory file.

  You can create a file called `deploy-cohesity-agent.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> deploy-cohesity-agent.yml
  ```

  Example playbook: `deploy-cohesity-agent.yml`
  ```yaml
  # => Cohesity Agent Management
  # =>
  # => Role: cohesity.ansible
  # =>

  # => Install the Cohesity Agent on each linux host
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
    # => We need to gather facts to determine the OS type of
    # => the machine
    gather_facts: yes
    become: true
    roles:
        - cohesity.ansible
    tasks:
      - name: Uninstall Cohesity Agent from each Linux Server
        include_role:
            name: cohesity.ansible
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: absent

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
