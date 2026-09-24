#!/bin/bash
set -e

echo "[*] Build Quartz..."
cd /home/ubuntu/wiki
npx quartz build

echo "[✅] Selesai."
