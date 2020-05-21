# Setup

[Go back to Documentation home page ](../README.md)

## Steps to install

* Make sure that the [prerequisites](pre-requisites.md) are installed.
* Install the Cohesity Ansible Role on the Ansible Control Machine using `ansible-galaxy` on the command line:
  ```
  ansible-galaxy install cohesity.cohesity_ansible_role
  ```
* All set! You can now reference the `cohesity.cohesity_ansible_role` role in your plays directly, like this:
  ```yaml
  roles:
      - cohesity.cohesity_ansible_role
  ```
