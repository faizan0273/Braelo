#!/bin/bash
# ---------------------------------------------------
# Project:        Braelo
# Date:           Aug 14, 2024
# Author:         Hamid
# ---------------------------------------------------
#
# Description:
# Install.sh file.
# ---------------------------------------------------
# Check for migrations in the 'users' app
if ! python manage.py showmigrations | grep '\[ \]'; then
    echo "No migrations detected. Stopping migration."
    exit 0
fi
# Remove the existing database file
rm -f db.sqlite3
# Run migrations for the 'users' app
python manage.py makemigrations users
python manage.py migrate
# Create a superuser with specified credentials if it doesn't exist
echo "
from users.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', password='admin')
" | python manage.py shell
echo "Setup complete."