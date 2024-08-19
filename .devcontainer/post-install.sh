#!/bin/bash
set -ex

# Convenience workspace directory for later use
WORKSPACE_DIR=$(pwd)

# upgrade pip
python -m pip install --upgrade pip
poetry install --sync

sudo mkdir ../von-network && sudo chown vscode:vscode ../von-network
sudo mkdir ../indy-tails-server && sudo chown vscode:vscode ../indy-tails-server
