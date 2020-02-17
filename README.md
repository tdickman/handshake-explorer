# Handshake Explorer

This is a block explorer for the [handshake](https://handshake.org) project.
It's built with python, django, and kubernetes. This is currently deployed to
[hnsxplorer](https://hnsxplorer.com).

## Requirements

* Docker

## Local Setup

```
git clone git@github.com:tdickman/handshake-explorer.git
docker-compose up
```

This will start the django app, and all dependent services. See the comments in
`docker-compose.yml` for more details. Most changes will be picked up
automatically, but any scss changes will require you to stop the app and run
the following:

```
docker-compose build
docker-compose up
```

## Deployment

We use skaffold to deploy this app to a kubernetes cluster.

```
PASSWORD=$(openssl rand -base64 32)
kubectl create secret generic db --from-literal=password=$PASSWORD
kubectl create secret generic django --from-literal=secret-key=SECRET_KEY
skaffold dev --port-forward
```
