#!/usr/bin/env bash
set -euo pipefail

if ! sudo docker info >/dev/null 2>&1; then
  sudo service docker start
fi
ready=0
for _ in $(seq 1 30); do
  if sudo docker info >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done
if [ "$ready" -ne 1 ]; then
  echo "Docker daemon did not become ready" >&2
  exit 1
fi
sudo chmod 666 /var/run/docker.sock
