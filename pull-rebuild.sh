#!/bin/bash
set -e
echo "=== Wiki Pull & Rebuild ==="
cd /home/ubuntu/wiki
echo "[1/3] Pulling from GitHub..."
git pull origin v5
echo "[2/3] Rebuilding Quartz..."
bash build_wiki.sh
echo "[3/3] Done! Wiki updated."
