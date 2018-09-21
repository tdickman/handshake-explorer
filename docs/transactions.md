# Transactions

This document contains notes on the different transaction types
used in handshake.

* [Reveal](http://localhost:8000/block/12589fe9cf320535eadbc1e570bdcc1365c225f9a6c9d2ee1cecd400a4b05e13)
* [Open](http://localhost:8000/block/c79504b17563bfee8ed47a4fb98b3661f9397741896ac362d1c56d4d93c6f5ba)
* [Register](http://localhost:8000/block/9561fc91070d07ba54f8c2b43310cc629c6df04a1b92816f2268e124efdf1a19)
* [Update](http://localhost:8000/block/e6c6d505ba2096fd773ad61e78f8b89769dd7e2e377073d4996d39fb6b905437)

## Structure

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

## Auction Process

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

