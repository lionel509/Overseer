#!/bin/bash
# Install Overseer CLI tool in the current (conda) environment
set -e

echo "[Overseer CLI] Installing dependencies..."
pip install -r requirements.txt

echo "[Overseer CLI] Installing CLI tool in editable mode..."
pip install -e .

echo "[Overseer CLI] Installation complete! Run 'overseer --mode local' to get started." 