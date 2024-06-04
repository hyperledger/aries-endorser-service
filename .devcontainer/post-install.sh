#!/bin/bash
set -ex

# Convenience workspace directory for later use
WORKSPACE_DIR=$(pwd)

# upgrade pip
python -m pip install --upgrade pip
poetry install --sync
