#!/bin/bash

HERE=$(dirname "${BASH_SOURCE}" | xargs realpath)

rsync -av $HERE/../ $1:mila-docs-chatbot --exclude sphinx-docs
ssh -t $1 sudo mila-docs-chatbot/install/install.sh
