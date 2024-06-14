# Basic time-saving repository for your sqlalchemy postgresql engine creation
### needs .env with following constants:
PG_HOST=
PG_PORT=
PG_USER=
PG_PASSWORD=
PG_DBNAME=
KINOPOISK_API_TOKEN=
FLASK_PORT=

## Dependency installation
Intsall different python's frameworks and libraries on your computer (will be better if you will use venv)
```
pip install -r requirements.txt
```

## Using venv (virtual enviroment)
Creating venv:
```
python -m venv <name_of_your_venv>
```
Activating venv:
```
source <name_of_your_venv>/bin/activate
```

## Launching a web application.
Also you need to create a docker container for database:
```
docker run -d --name <your_containrer_name> -p <your_port>:5432 -e POSTGRES_USER=<your_user> -e POSTGRES_PASSWORD=<your_password> -e POSTGRES_DB=<your_db_name> postgres
```

**Migrate tables to database**
```
flask db migrate -m "<your_migration_name>"
```
```
flask db upgrade
```

**Run application**
```
python app.py
```