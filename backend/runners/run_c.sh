#!/bin/sh
set -e
gcc -o /workspace/out /workspace/code.c
exec /workspace/out
