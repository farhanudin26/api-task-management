# SIMULATION TRIASE API

# Description

`alembic`: database migration for manage table

`api`: logic of configuration routers

`dtos`: data transfer object

`models`: model configuration

`repositories`: repository of specific business logic function

`services`: service of layer between operation and business logic

`tests`: test configuration

`utils`: reusable function

`static`: external assets directory


# Dependencies:
- [Python 3.12](https://www.python.org/) - Python 3.12
- [FastAPI](https://fastapi.tiangolo.com/) - Framework for Python
- [SQLAlchemy](https://www.sqlalchemy.org/) -  ORM Toolkit for SQL Database
- [MySQL](https://www.mysql.com/) - Database SQL

> Be carefull with python version.
> Always using environment like [anaconda](https://www.anaconda.com/)/[miniconda](https://docs.conda.io/en/latest/miniconda.html)/[virtualenv](https://virtualenv.pypa.io/en/latest/) for setup backend.
> Don't forget to activate environment.

Want to contribute? Great!

## Development

Create python env using miniconda/anaconda

```sh
conda create --name api-task-management
```

Activate python env

```sh
conda activate api-task-management
```

> Note:  activate environment and set python interpreter to your environment. if using vscode do `ctrl+shift+p` then write `python interpreter`, after that select the right environment
> After select python interpreter, kill terminal in vscode then add terminal to prevent environment still work in global

Duplicate .env.example and renamed it to .env

Fill this variable in .env
```sh
DB="mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
```

You can customize port of deploy web
```sh
PORT=5002
```

Install package

```sh
pip install -r requirements.txt
```

Running Application

```sh
uvicorn main:app --reload
```

Look endpoint list in (SWAGGER DOCUMENTATION)

```sh
http://localhost:8000/docs
```

## GENERATE KEY FOR PRIVATE_KEY, PUBLIC_KEY, REFRESH_PRIVATE_KEY

generate private key

```sh
openssl genrsa -out private.pem 2048
```

generate public key

```sh
openssl rsa -in private.pem -outform PEM -pubout -out public.pem 
```

generate private key for refresh

```sh
openssl genrsa -out private-refresh.pem 2048
```

## DATABASE SETUP - MIGRATION

duplicate alembic.ini.example and rename to alembic.ini

set sqlalchemy.url on alembic.ini with valid configuration

initial alembic

```sh
alembic init alembic
```

create migration file

```sh
alembic revision -m "create {name} table"
```

upgrade file

```sh
alembic upgrade head
```

upgrade file from exec container

```sh
docker exec -it <container_id_or_name> alembic upgrade head
```

downgrade latest file


```sh
alembic downgrade -1
```


running seeding data

```sh
python seeder.py
```

IGNORE TRACKING CHANGE ON DATA TEMPLATES EXCEL

```sh
git update-index --assume-unchanged data/templates/excel/Template_User.xlsx
```

```sh
git update-index --assume-unchanged data/templates/excel/Template_Create_Task.xlsx
```

```sh
git update-index --assume-unchanged data/templates/excel/Template_Permission_List.xlsx
```

```sh
git update-index --assume-unchanged data/templates/excel/Template_Project.xlsx
```

ACTIVE TRACKING

```sh
git update-index --no-assume-unchanged <POSITION/FILENAME>
```
