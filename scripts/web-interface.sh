#!/bin/bash

export MILA_BASE=/buster

source $MILA_BASE/venv/bin/activate
source $MILA_BASE/env
source $MILA_BASE/secrets

buster-gradio
