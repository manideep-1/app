#!/bin/sh
set -e
g++ -std=c++17 -o /workspace/out /workspace/code.cpp
exec /workspace/out
