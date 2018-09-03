# Local Setup

```
pipenv shell --three
pipenv install
```

Database:

```
docker run -p 5432:5432 postgres:10.5
psql -h localhost -U postgres -v ON_ERROR_STOP=1 --username postgres -d postgres <<-EOSQL
  CREATE USER hnsxplorer_dev;
  CREATE DATABASE hnsxplorer_dev;
  GRANT ALL PRIVILEGES ON DATABASE hnsxplorer_dev TO hnsxplorer_dev;
EOSQL
python manage.py migrate
```

Redis:

```
docker run -p 6379:6379 redis
```

# Running

```
cd hsdexplorer
python manage.py runserver 0.0.0.0:8000
celery -A hsdexplorer worker -l info -B  # -B is optional -> used if celery beat is enabled
```

# Deployment

```
PASSWORD=$(openssl rand -base64 32)
k create secret generic db --from-literal=password=$PASSWORD
k exec -it postgres-... bash
psql -v ON_ERROR_STOP=1 --username postgres -d postgres <<-EOSQL
  CREATE USER hnsxplorer_testnet with password '$PASSWORD';
  CREATE DATABASE hnsxplorer_testnet;
  GRANT ALL PRIVILEGES ON DATABASE hnsxplorer_testnet TO hnsxplorer_testnet;
EOSQL
skaffold run
```

# Examples

* [Reveal](http://localhost:8000/block/12589fe9cf320535eadbc1e570bdcc1365c225f9a6c9d2ee1cecd400a4b05e13)
* [Open](http://localhost:8000/block/c79504b17563bfee8ed47a4fb98b3661f9397741896ac362d1c56d4d93c6f5ba)
* [Register](https://hnsxplorer.com/block/9561fc91070d07ba54f8c2b43310cc629c6df04a1b92816f2268e124efdf1a19)
* [Update](https://hnsxplorer.com/block/e6c6d505ba2096fd773ad61e78f8b89769dd7e2e377073d4996d39fb6b905437)

# Transaction Structure

This contains a description of the structure of the covenant section of each
transaction type.

OPEN 2:

* nameHash -> sha3
* 0 -> int
* rawName -> str

BID 3:

* nameHash -> sha3
* ns.height -> little endian uint32 - indicates open block of auction
* rawName -> str
* hash(blind) -> ??

REVEAL 4:

* nameHash -> sha3
* ns.height -> little endian uint32 - indicates open block of auction
* nonce -> ??  # Blind hash

REDEEM:

* nameHash -> sha3
* ns.height -> little endian uint32 - indicates open block of auction

REGISTER:

* nameHash -> sha3
* ns.height -> little endian uint32 - indicates open block of auction

UPDATE:

* nameHash -> sha3
* ns.height -> little endian uint32 - indicates open block of auction
* resource -> ??

RENEW:

* nameHash -> sha3
* ns.height -> little endian uint32 - indicates open block of auction
* renewalBlock -> little endian uint32 - indicates open block of auction

# Auction Process

OPEN -(73 blocks)-> BID -(288 blocks)-> REVEAL|REDEEM -(576 blocks)-> Completed

Notes:
* Transaction value during the reveal phase == the amount of our actual bid
* First update sent after winning comes through as a 'register' event - it
  looks like this contains tld data that I am currently not parsing
* Not clear when we get our refund

# HSD-forked Interesting Functions

* lib/blockchain/chaindb.js:1833 - saveNames
* lib/blockchain/chain.js
* lib/node/http.js:172 - getCoinsByAddress

# Network Constants

Values for Testnet:

* Open period - 72 blocks (~6 hours) == treeInterval

Values:

* Mainnet - https://github.com/handshake-org/hsd/blob/master/lib/protocol/networks.js#L230
* Testnet - https://github.com/handshake-org/hsd/blob/master/lib/protocol/networks.js#L683

# Notes

* https://bootswatch.com/sandstone/
* Alternative theme: https://picnicss.com/tests

# TODO

* X Auctions by state
* X Address search tool
* Show mempool
* X Show address balance on transaction page
* Show raw transaction (or link to show) on tx page
* X Show transaction transition
* X Add height to transaction view
* X Fix timestamp in tx view
* X Show status of transaction (pending)
* Add ability to watch specific auctions and receive notifications
* Verify history processor handling if node restarts and has to resync from block 0
* Add time estimates to name tracker page
* Add about page with contact info
* List of active auctions
* API
