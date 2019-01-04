# How to use

## Getting Started
If you haven't used Ansible before, watch this [quick-start video](https://www.ansible.com/resources/videos/quick-start-video) to get started.

## Ansible Inventory
Make sure that your [Ansible Inventory File](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) is set up correctly.

  > **Tip:** What is the [Ansible Inventory File](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)?
  - Ansible works against multiple systems in your infrastructure at the same time. It does this by selecting a set of systems listed in Ansible’s inventory (default location: `/etc/ansible/hosts`).
  - You can also specify a different inventory file using the `-i <inventory_file>` option on the command line.
  - You can determine whether the inventory file is set up correctly by testing the connections to all the hosts: `ansible -m ping -i <inventory_file> all`

  * This is an example of the inventory file. This inventory is simple and has only one host group called `linux`, but typically, the inventory file will contain multiple host groups.
    ```ini
      [linux]
      10.2.46.95
      10.2.46.96
      10.2.46.97

      [linux:vars]
      ansible_user=root
    ```

  * If you plan to run Ansible tasks against Windows hosts, make sure that the [Windows hosts are set up correctly](https://www.ansible.com/blog/connecting-to-a-windows-host).

## Using the `cohesity.ansible` Role
* After [installing the Cohesity Ansible Role](setup.md), you can include the `cohesity.ansible` role and specific tasks, along with the supported variables, in your plays.

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
