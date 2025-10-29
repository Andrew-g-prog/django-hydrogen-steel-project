#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install -r requirements.txt

# collect static for WhiteNoise
python manage.py collectstatic --noinput
