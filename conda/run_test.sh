#!/bin/bash

set -euo pipefail

if [[ $(uname) =~ Linux ]]; then
    cd tests
    nosetests
fi

