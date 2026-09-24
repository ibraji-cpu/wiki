#!/bin/bash
cd /home/ubuntu/wiki
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/v5)
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$(date)] Changes detected, pulling and rebuilding..."
    git pull origin v5
    bash build_wiki.sh >> /var/log/wiki-auto-rebuild.log 2>&1
    echo "[$(date)] Rebuild done."
else
    echo "[$(date)] No changes."
fi
