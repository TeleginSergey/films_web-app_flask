#!/bin/bash

export PG_HOST=127.0.0.1
export PG_PORT=5432
export PG_USER=test
export PG_PASSWORD=test
export PG_DBNAME=postgres
export KINOPOISK_API_TOKEN=DFQPW7A-F45M9AB-G8J4GRQ-CCV2QAB
export FLASK_PORT=4000
python3 -m unittest discover -s $1
