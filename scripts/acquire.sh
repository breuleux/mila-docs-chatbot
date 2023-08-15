#!/bin/bash

export MILA_BASE=/buster

source $MILA_BASE/venv/bin/activate
source $MILA_BASE/env
source $MILA_BASE/secrets

buster-acquire-sphinx \
    $MILA_BASE/config/sphinx-docs.yaml \
    --base $MILA_BASE/sphinx-docs \
    --db $MILA_BASE/documents.db
