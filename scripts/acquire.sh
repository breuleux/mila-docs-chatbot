#!/bin/bash

export MILA_BASE=/buster

source $MILA_BASE/code/venv/bin/activate
source $MILA_BASE/code/config/env
source $MILA_BASE/code/config/secrets

buster-acquire-sphinx \
    $MILA_BASE/code/config/sphinx-docs.yaml \
    --base $MILA_BASE/sphinx-docs \
    --db $MILA_BASE/documents.db

systemctl restart buster-web.service
