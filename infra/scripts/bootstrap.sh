#!/usr/bin/env bash
set -euo pipefail

poetry run python -m app.workflows.bootstrap
