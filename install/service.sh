#!/bin/bash

HERE=$(dirname "${BASH_SOURCE}" | xargs realpath)

cp -f $HERE/../systemd/*.service /etc/systemd/system/
cp -f $HERE/../systemd/*.timer /etc/systemd/system/

systemctl daemon-reload

systemctl start buster-regen-docs.timer
systemctl enable buster-regen-docs.timer

systemctl start buster-web.service
systemctl enable buster-web.service
