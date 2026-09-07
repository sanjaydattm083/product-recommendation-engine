#!/usr/bin/env bash
set -euo pipefail
cd /home/ubuntu/product-recommendation-engine
git fetch origin
git reset --hard origin/main
./venv/bin/pip install -r requirements.txt
pm2 restart repeatorder-api --update-env
pm2 save
