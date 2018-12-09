#!/bin/bash

set -eux -o pipefail

cd "$1"

pip install -e."[dev]"

pytest -v
