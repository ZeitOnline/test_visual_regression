#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR  # pytest is very sensitive to the CWD
if [ ! -f bin/python ]; then
    virtualenv .
fi
bin/pip install --no-deps -r ./requirements.txt
bin/pytest $*
