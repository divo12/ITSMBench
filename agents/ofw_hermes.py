"""Harbor adapter for the local Hermes harness checkout."""

from __future__ import annotations

import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import override

import yaml
from harbor.agents.installed import hermes as harbor_hermes
from harbor.agents.installed.hermes import Hermes
from harbor.environments.base import BaseEnvironment

HERMES_SOURCE = Path("/Users/divyansh/HermesHarness")
HERMES_REVISION = subprocess.run(
    ("git", "rev-parse", "HEAD"),
    cwd=HERMES_SOURCE,
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

harbor_hermes._NATIVE_PROVIDERS["openai"] = (
    "openai-api",
    ["OPENAI_API_KEY"],
)


class OfwHermes(Hermes):
    @staticmethod
    @override
    def name() -> str:
        return "ofw-hermes"

    @override
    def version(self) -> str:
        return HERMES_REVISION

    @staticmethod
    @override
    def _build_config_yaml(model: str) -> str:
        config = yaml.safe_load(Hermes._build_config_yaml(model))
        config["plugins"] = {
            "enabled": ["observability/langfuse"],
            "disabled": [],
        }
        return yaml.safe_dump(config, default_flow_style=False)

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        with tempfile.NamedTemporaryFile(suffix=".tar.gz") as archive:
            subprocess.run(
                (
                    "git",
                    "archive",
                    "--format=tar.gz",
                    f"--output={archive.name}",
                    HERMES_REVISION,
                ),
                cwd=HERMES_SOURCE,
                check=True,
            )
            await environment.upload_file(archive.name, "/tmp/hermes-source.tar.gz")

        await self.exec_as_root(
            environment,
            command=(
                "set -euo pipefail; "
                "apt-get update; "
                "DEBIAN_FRONTEND=noninteractive apt-get install -y "
                "ca-certificates curl git ripgrep xz-utils; "
                "curl -LsSf https://astral.sh/uv/install.sh | "
                "UV_UNMANAGED_INSTALL=/usr/local/bin sh; "
                "mkdir -p /opt/hermes-source; "
                "tar -xzf /tmp/hermes-source.tar.gz -C /opt/hermes-source; "
                "cd /opt/hermes-source; "
                "UV_PROJECT_ENVIRONMENT=/opt/hermes-source/venv "
                "uv sync --locked; "
                "uv pip install --python /opt/hermes-source/venv/bin/python "
                + shlex.quote("langfuse>=4.7,<5")
                + "; "
                "printf '%s\\n' '#!/bin/sh' "
                "'exec /opt/hermes-source/venv/bin/python "
                "/opt/hermes-source/hermes \"$@\"' > /usr/local/bin/hermes; "
                "chmod +x /usr/local/bin/hermes; "
                "hermes --version"
            ),
            timeout_sec=900,
        )
