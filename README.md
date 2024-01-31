# Quickstart

## Install

```bash
pip install -e .
```

Reproducible install:

```bash
pip install -r pinned-requirements.txt
```


## Configure

* Copy `config/mila-config.yaml` to `config.yaml` and adapt to your use case.
* Set `OPENAI_API_KEY` to your OpenAI API key.
  * Alternatively, you can set `openai: api_key: API_KEY` in the YAML configuration file.

Optionally, set `BUSTER_CONFIG` to the path to the configuration, which will spare you from having to write `--config` all the time.


## Acquire documentation

Currently, there is only an acquirer for Sphinx documentation.

```bash
buster_service --config config.yaml acquire sphinx
```


## Start the web service

```bash
buster_service --config config.yaml web
```


## Ansible

To install the service on a machine using ansible, see `ansible/README.md`.
