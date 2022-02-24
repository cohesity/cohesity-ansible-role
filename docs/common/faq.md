# Frequently Asked Questions

[Go back to Documentation home page ](../README.md)

### Do the Ansible Modules support Active Directory based Cohesity Accounts?
Yes.  You can configure your domain specific credentials in following formats.
- username@AD.domain.com        # AD User
- AD.domain.com/username@tenant # AD Tenant User
- LOCAL/username@tenant         # Local Tenant User
- Domain/username (Will be deprecated in future)

### What privileges does the Active Directory based account require?
The Active Directory account should include administrator level privileges on the cluster

