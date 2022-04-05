#!/bin/sh
set -e  # Exit immediately if a command exits with a non-zero status
set -x  # all executed commands are printed to the terminal.

case "$1" in
    run)
        python3 app.py
    ;;
    *)
        exec $@
    ;;
esac