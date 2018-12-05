# How to use

## Getting Started
If you haven't used Ansible before, you may want to watch this [quick-start video](https://www.ansible.com/resources/videos/quick-start-video) to get started.

## Ansible Inventory
Please make sure that your [Ansible Inventory File](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) is setup correctly.

  > **Tip:** What is [Ansible Inventory File](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)?
  - Ansible works against multiple systems in your infrastructure at the same time. It does this by selecting a set of systems listed in Ansible’s inventory (default location: `/etc/ansible/hosts`).
  - You can also specify a different inventory file using the `-i <inventory_file>` option on the command line.
  - You can test if the inventory file is setup correctly by testing connection to all the hosts: `ansible -m ping -i <inventory_file> all`

  * Here is an example of the inventory file. This inventory is simple and has only one host group called `linux`. Typically the inventory file will contain multiple host groups.
    ```ini
      [linux]
      10.2.46.95
      10.2.46.96
      10.2.46.97

      [linux:vars]
      ansible_user=root
    ```

  * If you plan to run Ansible tasks against Windows hosts, please make sure that the [windows hosts are setup correctly](https://www.ansible.com/blog/connecting-to-a-windows-host).

## Using `cohesity.ansible` Role
* After [installing Cohesity Ansible Role](setup.md), you can include the `cohesity.ansible` role and specific tasks along with the supported variables in your plays.

* Here is an example playbook that uninstalls the Cohesity agent (only if present), then installs the latest Cohesity agent on all the `linux` hosts in the inventory file.

  You can create a file called `deploy-cohesity-agent.yml`, add the contents below and then run this playbook using `ansible-playbook`:
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
