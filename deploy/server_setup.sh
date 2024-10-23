#!/usr/bin/env bash

set -e

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/mhddanny/Project_New.git'

PROJECT_BASE_PATH='/usr/local/apps'
VIRTUALENV_BASE_PATH='/usr/local/virtualenvs'

# Set Ubuntu Language
locale-gen en_GB.UTF-8

# Install Python, SQLite and pip
echo "Installing dependencies..."
apt-get update
apt-get install -y python3-dev python3-venv python-pip supervisor postgresql postgresql-contrib nginx git

mkdir -p $PROJECT_BASE_PATH
git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH/Project_New

mkdir -p $VIRTUALENV_BASE_PATH
python3 -m venv $VIRTUALENV_BASE_PATH/Project_New

$VIRTUALENV_BASE_PATH/Project_New/bin/pip install -r $PROJECT_BASE_PATH/Project_New/requirements.txt

# Run migrations
cd $PROJECT_BASE_PATH/Project_New/src

# Setup Supervisor to run our uwsgi process.
cp $PROJECT_BASE_PATH/Project_New/deploy/supervisor_projectCart.conf /etc/supervisor/conf.d/projectCart.conf
supervisorctl reread
supervisorctl update
supervisorctl restart Project_New

# Setup nginx to make our application accessible.
cp $PROJECT_BASE_PATH/Project_New/deploy/nginx_projectCart.conf /etc/nginx/sites-available/projectCart.conf
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/projectCart.conf /etc/nginx/sites-enabled/projectCart.conf
systemctl restart nginx.service

echo "DONE! :)"