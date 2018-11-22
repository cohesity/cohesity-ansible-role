# Setup

## Steps to install

* Please make sure that the [pre-requisites](pre-requisites.md) are installed.
* Create a file called `requirements.yml` on the Ansible Control Machine and add the contents below.
  ```
  # Install Cohesity Ansible role from GitHub
  - name: cohesity.ansible
    src: https://github.com/cohesity/cohesity-ansible-role
  ```
* Install the Cohesity Ansible role on the Ansible Control Machine using `ansible-galaxy`.
  ```
  ansible-galaxy install -r requirements.yml
  ```
* All set! You can now reference `cohesity.ansible` role in your plays directly.
  ```yaml
  roles:
      - cohesity.ansible
  ```
