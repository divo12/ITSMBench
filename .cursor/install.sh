#!/usr/bin/env bash
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/0.12.19/install.sh | env UV_NO_MODIFY_PATH=1 sh
fi
uv tool install "harbor[daytona]==0.23.0"

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
test "$ready" -eq 1

sudo docker pull public.ecr.aws/f8p0s4x7/taskgen-emulator@sha256:a3dc8a1f0c354e973937d95550bb1e67a0e4cfd810bdddc34191317d60a8b5ab
sudo docker tag public.ecr.aws/f8p0s4x7/taskgen-emulator@sha256:a3dc8a1f0c354e973937d95550bb1e67a0e4cfd810bdddc34191317d60a8b5ab harbor.local/taskgen-emulator:a3dc8a1f0c35
sudo docker pull public.ecr.aws/f8p0s4x7/taskgen-emulator:cat-1ab2a6b42823
sudo docker tag public.ecr.aws/f8p0s4x7/taskgen-emulator:cat-1ab2a6b42823 harbor.local/taskgen-emulator:cat-1ab2a6b42823
sudo docker pull public.ecr.aws/docker/library/ubuntu:24.04
sudo docker pull public.ecr.aws/docker/library/node:22-bookworm-slim
sudo docker pull public.ecr.aws/docker/library/python:3.13-slim-bookworm
sudo service docker stop
