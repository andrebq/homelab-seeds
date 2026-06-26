#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///

"""
Deploy the jupyter stack to Portainer.

Required env vars:
  PORTAINER_URL         Base URL of the Portainer instance (e.g. https://portainer:9443)
  PORTAINER_ENDPOINT_ID Portainer endpoint (environment) ID

Optional env vars:
  PORTAINER_STACK_NAME  Stack name (default: jupyter)
  PORTAINER_CA_CERT     Path to a CA cert bundle to verify Portainer's TLS certificate.
                        Set to "false" to disable verification entirely (not recommended).
"""

import os
import subprocess
import sys
from pathlib import Path

import warnings

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SECRETS = REPO_ROOT / "scripts" / "secrets"
API_KEY_AGE = REPO_ROOT / "nba" / "PORTAINER_API_KEY.age"
TOKEN_AGE = Path(__file__).resolve().parent / "TOKEN.age"
COMPOSE_FILE = Path(__file__).resolve().parent / "docker-compose.yml"


def decrypt(path: Path) -> str:
    result = subprocess.run(
        ["uv", "run", "--script", str(SECRETS), "decrypt", "-i", str(path)],
        capture_output=True,
    )
    if result.returncode != 0:
        sys.exit(f"error decrypting {path}:\n{result.stderr.decode()}")
    return result.stdout.decode().strip()


def main() -> None:
    portainer_url = os.environ.get("PORTAINER_URL")
    endpoint_id = os.environ.get("PORTAINER_ENDPOINT_ID")
    stack_name = os.environ.get("PORTAINER_STACK_NAME", "jupyter")

    if not portainer_url:
        sys.exit("error: PORTAINER_URL env var is required")
    if not endpoint_id:
        sys.exit("error: PORTAINER_ENDPOINT_ID env var is required")

    ca_cert = os.environ.get("PORTAINER_CA_CERT", "false")
    if ca_cert.lower() == "false":
        ssl_verify = False
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    else:
        ssl_verify = ca_cert

    api_key = decrypt(API_KEY_AGE)
    token = decrypt(TOKEN_AGE)
    compose_content = COMPOSE_FILE.read_text()

    url = f"{portainer_url.rstrip('/')}/api/stacks"
    params = {"type": 2, "method": "string", "endpointId": endpoint_id}
    headers = {"X-API-Key": api_key}
    payload = {
        "name": stack_name,
        "stackFileContent": compose_content,
        "env": [{"name": "JUPYTER_TOKEN", "value": token}],
    }

    resp = requests.post(url, params=params, headers=headers, json=payload, verify=ssl_verify)
    if not resp.ok:
        sys.exit(f"error: Portainer API returned {resp.status_code}:\n{resp.text}")

    data = resp.json()
    print(f"stack '{stack_name}' created (id={data.get('Id')})")


if __name__ == "__main__":
    main()
