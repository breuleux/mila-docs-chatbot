#!/bin/bash

set -e

HERE=$(dirname "${BASH_SOURCE}" | xargs realpath)

sudo $HERE/assudo.sh
$HERE/setup.sh
sudo chown -R buster /buster
sudo chgrp -R buster /buster
sudo $HERE/service.sh
