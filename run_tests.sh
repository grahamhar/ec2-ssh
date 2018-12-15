#!/bin/bash

set -eux -o pipefail

cd "$1"

pip install -q -e."[dev]"

pytest -v --html=./build-results/report.html
