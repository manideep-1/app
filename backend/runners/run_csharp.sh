#!/bin/sh
set -e
# /workspace has Program.cs (mounted). /app has pre-restored project.
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
export DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE=1
export DOTNET_CLI_HOME=/tmp
cp /workspace/Program.cs /app/Program.cs
exec dotnet run --project /app/App.csproj --no-restore
