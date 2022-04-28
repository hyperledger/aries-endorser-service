# Aries - Endorser Service

This repository provides an Endoser agent, based on [Aries Cloudagent Pythong (or Aca-Py)](https://github.com/hyperledger/aries-cloudagent-python).

Information about Aca-Py's Endorser support can be found [here](https://github.com/hyperledger/aries-cloudagent-python/blob/main/Endorser.md).

The Aca-Py Alice/Faber demo also demonstrates the use of the Endorser feature, as described [here](https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/Endorser.md).

## Running Locally

To get up and running quicky, open a bash shell and run the following:

```bash
git clone https://github.com/bcgov/aries-endorser-service.git
cd aries-endorser-service/docker
./manage build
./manage start --logs
```

To shut down the service:

```bash
<ctrl-c>
./manage rm
```

By default, the Endorser runs against the BCovrin Test ledger (http://test.bcovrin.vonx.io/).  To run against a different ledger, start using the `GENESIS_URL` parameter:

```bash
GENESIS_URL=<path to genesis txn> ./manage start --logs
```

For example, the SOVRIN staging ledger's transactions can be found [here](https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_sandbox_genesis).

By default, the `./manage` script will use a random seed to generate the Endorser's public DID.  Author agents will need to know this public DID in order to create transactions for endorsement.  If you need to start the Endorser using a "well known DID" you can start with the `ENDORSER_SEED` parameter:

```bash
ENDORSER_SEED=<your 32 char seed> ./manage start --logs
```
