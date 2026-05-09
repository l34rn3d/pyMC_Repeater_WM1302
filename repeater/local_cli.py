"""
CLI client for pyMC Repeater.
Connects to an already-running repeater daemon via its HTTP API.
Reads admin password and HTTP port from the local config.yaml automatically.
"""

import sys


CONFIG_PATHS = [
    "/etc/pymc_repeater/config.yaml",
    "config.yaml",
]


def _load_config(config_path=None):
    """Load repeater config.yaml, trying common paths."""
    import yaml
    from pathlib import Path

    paths = [config_path] if config_path else CONFIG_PATHS
    for p in paths:
        path = Path(p)
        if path.is_file():
            with open(path) as f:
                return yaml.safe_load(f) or {}
    return {}


def run_client_cli(host: str = "127.0.0.1", port: int = 8000, password: str = ""):
    """
    Standalone CLI client that connects to a running repeater's HTTP API.
    """
    import urllib.request
    import urllib.error
    import json

    base_url = f"http://{host}:{port}"

    # Authenticate to get JWT token
    token = None
    if password:
        try:
            auth_data = json.dumps({
                "username": "admin",
                "password": password,
                "client_id": "pymc-cli",
            }).encode()
            req = urllib.request.Request(
                f"{base_url}/auth/login",
                data=auth_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                token = result.get("token") or result.get("data", {}).get("token")
        except urllib.error.URLError as e:
            print(f"Error: Cannot connect to repeater at {base_url} — {e.reason}")
            sys.exit(1)
        except Exception as e:
            print(f"Authentication failed: {e}")
            sys.exit(1)

    if not token:
        print("Error: Authentication failed. Check password or repeater status.")
        sys.exit(1)

    print(f"\npyMC Repeater CLI (connected to {base_url})")
    print("Type 'help' for available commands, 'exit' to quit.\n")

    while True:
        try:
            command = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not command:
            continue
        if command in ("exit", "quit"):
            break

        try:
            payload = json.dumps({"command": command}).encode()
            req = urllib.request.Request(
                f"{base_url}/api/cli",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                if result.get("success"):
                    print(result["data"]["reply"])
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}")
        except urllib.error.URLError as e:
            print(f"Connection error: {e.reason}")
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Entry point for pymc-cli command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Connect to a running pyMC Repeater and issue CLI commands"
    )
    parser.add_argument(
        "--config", default=None,
        help="Path to config.yaml (auto-detected if not set)",
    )
    parser.add_argument(
        "--host", default=None,
        help="Repeater HTTP host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port", type=int, default=None,
        help="Repeater HTTP port (default: from config or 8000)",
    )
    args = parser.parse_args()

    # Load config to get password and port automatically
    config = _load_config(args.config)
    repeater_cfg = config.get("repeater", {})
    security_cfg = repeater_cfg.get("security", {})
    password = security_cfg.get("admin_password", "")

    if not password:
        print("Error: No admin_password found in config.yaml.")
        print("Searched: " + ", ".join(CONFIG_PATHS))
        sys.exit(1)

    host = args.host or "127.0.0.1"
    port = args.port or config.get("http", {}).get("port", 8000)

    run_client_cli(host=host, port=port, password=password)


if __name__ == "__main__":
    main()
