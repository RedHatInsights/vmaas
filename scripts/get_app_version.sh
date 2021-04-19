#!/bin/sh

if [[ -x "$(command -v python3)" ]]
then
    python3 -c 'from common.constants import VMAAS_VERSION;print(VMAAS_VERSION)'
fi
