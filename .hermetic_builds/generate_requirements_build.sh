#!/bin/bash

pip3 install pip-tools pybuild-deps
pip3 install "pip<25"
cd /var/tmp

# We do not have to generate new requirements file as we have all versions pinned in requirements.txt
pybuild-deps compile --generate-hashes requirements.txt -o requirements-build.txt

pip-compile requirements-build.in --allow-unsafe --generate-hashes -o requirements-extra.txt
