#!/usr/bin/env bash
set -euo pipefail
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-pos_project.settings.development}
python manage.py makemigrations core pos
python manage.py migrate
python manage.py loaddata fixtures/sample_data.json
