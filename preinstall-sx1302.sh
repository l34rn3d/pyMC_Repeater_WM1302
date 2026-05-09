#!/bin/bash
# Pre-install helper for WM1302/SX1302 concentrator installs.
# Run this after cloning and before `sudo ./manage.sh install` so the service
# can start far enough to expose the web setup wizard.

set -euo pipefail

CONFIG_TEMPLATE="config.yaml.example"

if [ ! -f "$CONFIG_TEMPLATE" ]; then
    echo "Error: $CONFIG_TEMPLATE not found. Run this from the pyMC_Repeater repo root." >&2
    exit 1
fi

python3 - <<'PY'
from pathlib import Path

path = Path("config.yaml.example")
lines = []
for line in path.read_text().splitlines():
    if line.startswith("radio_type:"):
        lines.append('radio_type: "sx1302"')
    else:
        lines.append(line)
path.write_text("\n".join(lines) + "\n")
PY

echo "Updated $CONFIG_TEMPLATE for SX1302/WM1302 bootstrap install."
echo "Next: sudo ./manage.sh install"
