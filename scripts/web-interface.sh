#!/bin/bash

export MILA_BASE=/buster

source $MILA_BASE/code/venv/bin/activate
source $MILA_BASE/code/config/env
source $MILA_BASE/code/config/secrets

buster-gradio
