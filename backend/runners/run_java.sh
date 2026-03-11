#!/bin/sh
set -e
# Compile in /workspace (mounted); then run with stdin/stdout
javac -d /workspace /workspace/Main.java
exec java -cp /workspace Main
