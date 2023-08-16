#!/bin/bash

set -e

HERE=$(dirname "${BASH_SOURCE}" | xargs realpath)

mkdir -p /buster
cp -r $HERE/.. /buster/code
cd /buster/code

# Set up virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -U pip
pip install poetry

# Install buster
pip install -e .
