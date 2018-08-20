# Setup

```
pipenv shell --three
pipenv install --skip-lock
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

OPEN -(? blocks)-> BID -(? blocks)-> REVEAL|REDEEM ->

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

* Auctions by state
* Address search tool
* Show mempool
* Show block in transaction view (block tx was processed in)
* Show address balance on transaction page
* Show raw transaction (or link to show) on tx page
* Show transaction transition
