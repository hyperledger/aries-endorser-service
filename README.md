# Aries - Endorser Service

This repository provides an Endoser agent, based on [Aries Cloudagent Python (or Aca-Py)](https://github.com/hyperledger/aries-cloudagent-python).

Information about Aca-Py's Endorser support can be found [here](https://github.com/hyperledger/aries-cloudagent-python/blob/main/Endorser.md).

The Aca-Py Alice/Faber demo also demonstrates the use of the Endorser feature, as described [here](https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/Endorser.md).

This repository is a work in progress, see [this document](https://hackmd.io/hWMLdpu7SBuopNag4mTbcg?view) for the on-going requirements and design.

## Running Locally

To get up and running quicky, open a bash shell and run the following:

```bash
git clone https://github.com/bcgov/aries-endorser-service.git
cd aries-endorser-service/docker
./manage build
./manage start --logs
```

You can open the Endorser Admin API in your browser at http://localhost:5050/endorser/docs - you will need to authenticate using the configured id and password (endorser-admin/change-me).  (The webhooks api is at http://localhost:5050/webhook/docs, although you shouldn't need to use this one directly.)

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

## Testing - Integration tests using Behave

This repository includes integration tests implemented using Behave.

When you start the endorser service, you can optionally start an additional Author agent which is used for testing:

```bash
./manage start-bdd --logs
```

The Author agent (which is configured as multi-tenant) exposes its Admin API on http://localhost:8061/api/doc

Open a second bash shell (cd to the directory where you have checked out this repository) and run:

```bash
virtualenv venv
source ./venv/bin/activate
pip install -r endorser/requirements.txt
cd docker
```

(Note that the above are one-time commands)

To run the BDD tests just run:

```bash
./manage run-bdd

```

(Note that this runs tests on your local rather than in a docker container, this may get updated at some point ...)

## Testing - Other

You can also test using [traction](https://github.com/bcgov/traction).

Open a bash shell and startup the endorser services:

```bash
git clone https://github.com/bcgov/aries-endorser-service.git
cd aries-endorser-service/docker
./manage build
# note we start with a "known" endorser DID
ENDORSER_SEED=testendorserseed_123123123123123 ./manage start --logs
```

Then open a separate bash shell and run the following:

```bash
git clone https://github.com/bcgov/traction.git
cd traction/scripts
git checkout endorser-integration
cp .env-example .env
docker-compose build
docker-compose up
```

Then open up yet another bash shell and run the traction integration tests.  Traction tenants will connect to the endorser service for creating schemas, credential definitions etc.

```bash
cd <traction/scripts directory from above>
docker exec scripts_traction-api_1 pytest --asyncio-mode=strict -m integtest
```

... or you can run individual tests like this:

```bash
docker exec scripts_traction-api_1 pytest --asyncio-mode=strict -m integtest tests/integration/endpoints/routes/test_tenant.py::test_tenant_issuer
```

Traction integration tests create new tenants for each test, so you can rebuild/restart the endorser service without having to restart traction.
