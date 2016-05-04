# Conversions-backend
Backend code for diploma thesis project on adaptive educational app

# How to

The app requires Python 3.5.1 or newer, PostgreSQL 9.4 or newer. 

1. Install dependencies listed in `requirements.txt`.

2. Set your database URL to `DATABASE_URL` env variable.

3. Initialize the db schema and load questions to database by running `initrun.sh` script.

4. Run the server with `python run.py run` (or alternatively `gunicorn run:app` when using *gunicorn* as a http server).
