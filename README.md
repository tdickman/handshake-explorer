# Handshake Explorer

This is a block explorer for the [handshake](https://handshake.org) project.
It's built with python, django, and kubernetes. This is currently deployed to
[hnsxplorer](https://hnsxplorer.com).

## Requirements

* Python 3.5+
* Pipenv
* Docker
* pysql
* Running copy of [hsd](https://github.com/handshake-org/hsd)

## Local Setup

```
git clone git@github.com:tdickman/handshake-explorer.git
pipenv shell --three
pipenv install
```

This project uses postgres to store and query certain blockchain information
that is not directly accessible using the handshake api. It also uses redis to
store queue information for the background celery tasks that retrieve this
data.

Database:

```
docker run -d -p 5432:5432 postgres:10.5
psql -h localhost -U postgres -v ON_ERROR_STOP=1 --username postgres -d postgres <<-EOSQL
  CREATE USER hnsxplorer_dev;
  CREATE DATABASE hnsxplorer_dev;
  GRANT ALL PRIVILEGES ON DATABASE hnsxplorer_dev TO hnsxplorer_dev;
EOSQL
python hsdexplorer/manage.py migrate
```

Redis:

```
docker run -d -p 6379:6379 redis
```

## Running

```
cd hsdexplorer
python manage.py compilescss
python manage.py runserver 0.0.0.0:8000
celery -A hsdexplorer worker -l info -B  # -B is optional -> used if celery beat is enabled
```

## Deployment

We use skaffold to deploy this app to a kubernetes cluster.

```
PASSWORD=$(openssl rand -base64 32)
kubectl create secret generic db --from-literal=password=$PASSWORD
kubectl create secret generic django --from-literal=secret-key=SECRET_KEY
k exec -it postgres-... bash
psql -v ON_ERROR_STOP=1 --username postgres -d postgres <<-EOSQL
  CREATE USER hnsxplorer_testnet with password '$PASSWORD';
  CREATE DATABASE hnsxplorer_testnet;
  GRANT ALL PRIVILEGES ON DATABASE hnsxplorer_testnet TO hnsxplorer_testnet;
EOSQL
skaffold run
```
