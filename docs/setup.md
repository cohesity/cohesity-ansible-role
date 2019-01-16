# Setup

## Steps to install

* Make sure that the [prerequisites](pre-requisites.md) are installed.
* Create a file called `requirements.yml` on the Ansible Control Machine and add these lines to the file:
  ```
  # Install Cohesity Ansible role from GitHub
  - name: cohesity.ansible
    src: https://github.com/cohesity/cohesity-ansible-role
  ```
* Install the Cohesity Ansible Role on the Ansible Control Machine using `ansible-galaxy` on the command line:
  ```
  ansible-galaxy install -r requirements.yml
  ```
* All set! You can now reference the `cohesity.ansible` role in your plays directly, like this:
  ```yaml
  roles:
      - cohesity.ansible
  ```
