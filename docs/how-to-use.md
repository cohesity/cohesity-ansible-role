# How to use

* After installation of the Role, you can import Cohesity Ansible Modules into your plays as below

  ```yaml
  roles:
      - cohesity.ansible
  ```

* To leverage a Role Task, you can include the role and specific task along with supported variables.

  ```yaml
  # Example to include the agent installation on Linux
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
  ```
