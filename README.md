# PROPER STEPS TO SETUP

## Pre-Setup
1. pip install virtualenv

## Setup
1. git clone https://github.com/zainul1996/Flask-Heroku-Boilerplate.git && cd Flask-Heroku-Boilerplate && rm -rf .git
2. virtualenv venv && source venv/bin/activate
3. pip install flask gunicorn

## Heroku
1. Go to https://dashboard.heroku.com/apps
2. Create new app _(take note of the project name)_

## Push
1. git init && git add . && git commit -m "init"
4. heroku login
5. heroku git:remote -a {***your-project-name***} _(use heroku project name)_
6. git push heroku master
