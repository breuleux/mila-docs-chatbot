
# Install via ansible

## Roles

Install the role `pyservice` which is hosted at `https://github.com/breuleux/ansible-role-pyservice`

Versions of the roles are implemented as tags on the repo, for example tag `v0.1.0`.


## Playbook

Use `playbooks/install.yml`


## Inventory

Here is an example of inventory to use with this role. Set `<VARIABLE>` to its proper value. Variables marked with SECRET are secrets and should be encrypted.

```
all:
  vars:
    app_name: buster
    app_module: buster_service  # Do not change this one
    app_user: buster
    app_config_dict:
      grizzlaxy:
        port: <PORT>
        host: <HOSTNAME>
        ssl:
          enabled: true
        oauth:
          enabled: true
    app_secrets_dict:
      openai:
        api_key: <OPENAI_API_KEY (SECRET!)>
        grizzlaxy:
          oauth:
            environ:
              GOOGLE_CLIENT_ID: <GOOGLE_CLIENT_ID (SECRET!)>
              GOOGLE_CLIENT_SECRET: <GOOGLE_CLIENT_SECRET (SECRET!)>
    app_ssl_cert: <SSL_CERT_CONTENT (SECRET!)>
    app_ssl_key: <SSL_KEY_CONTENT (SECRET!)>
```
