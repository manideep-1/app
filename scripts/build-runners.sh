#!/usr/bin/env bash
# Build all code-runner Docker images required for code execution.
# Run from repo root. Requires Docker to be running.
# Usage: ./scripts/build-runners.sh   or:  bash scripts/build-runners.sh

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNERS="${ROOT}/backend/runners"

echo "Building runner images (context: backend/runners) ..."

build_one() {
  local lang=$1
  local df=$2
  local img=$3
  echo "  Building ${img} ..."
  docker build -t "${img}" -f "${RUNNERS}/${df}" "${RUNNERS}"
}

build_one "Python"    "Dockerfile.python"    "ifelse-runner-python"
build_one "JavaScript" "Dockerfile.javascript" "ifelse-runner-javascript"
build_one "Java"      "Dockerfile.java"      "ifelse-runner-java"
build_one "C++"       "Dockerfile.cpp"       "ifelse-runner-cpp"
build_one "C"         "Dockerfile.c"         "ifelse-runner-c"
build_one "Go"        "Dockerfile.go"        "ifelse-runner-go"
build_one "C#"        "Dockerfile.csharp"    "ifelse-runner-csharp"
build_one "TypeScript" "Dockerfile.typescript" "ifelse-runner-typescript"

echo "Done. Runner images: ifelse-runner-python, ifelse-runner-javascript, ifelse-runner-java, ifelse-runner-cpp, ifelse-runner-c, ifelse-runner-go, ifelse-runner-csharp, ifelse-runner-typescript"
echo "Start the backend (and ensure Docker is running) to use code execution."
