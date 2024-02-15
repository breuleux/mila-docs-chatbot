
# Ansible role to install mila docs

## Requirements

Requires the role `pyservice` which is hosted at `https://github.com/breuleux/ansible-role-pyservice` (the dependency should be properly defined in the metadata).


## Inventory

Here is an example of inventory to use with this role. Set `<VARIABLE>` to its proper value. Variables marked with SECRET are secrets and should be encrypted.

```
all:
  vars:
    buster_name: buster
    buster_user: buster
    buster_repo: https://github.com/breuleux/mila-docs-chatbot
    buster_tag: auto

    buster_port: 8000     # Can override
    buster_host: 0.0.0.0  # Can override

    buster_openai_api_key: <OPENAI_API_KEY (SECRET!)>

    buster_ssl_enabled: <WHETHER SSL IS ENABLED>
    buster_ssl_cert: <SSL_CERT_CONTENT (SECRET!)>
    buster_ssl_key: <SSL_KEY_CONTENT (SECRET!)>

    buster_oauth_enabled: <WHETHER OAUTH IS ENABLED>
    buster_google_client_id: <GOOGLE_CLIENT_ID (SECRET!)>
    buster_google_client_secret: <GOOGLE_CLIENT_SECRET (SECRET!)>

    buster_sentry_enabled: <WHETHER SENTRY IS ENABLED>
```
