import json
import time
import os
import pprint
import random
import time

from behave import *
from starlette import status

from util import (
    authenticate_endorser_service,
    call_endorser_service,
    call_agency_service,
    call_author_service,
    GET,
    POST,
    HEAD,
    ENDORSER_URL_PREFIX,
)

MAX_INC = 5


@given('the endorser service is running')
def step_impl(context):
    # check that the endorser service is running
    endorser_status = call_endorser_service(context, GET, "/")
    assert endorser_status["status"] == "ok", pprint.pp(endorser_status)

    # authenticate the service and save our auth token
    endorser_auth_status = authenticate_endorser_service(context)
    assert endorser_auth_status["Authorization"].startswith("Bearer "), pprint.pp(endorser_auth_status)


@given('the endorser has a well-known public DID')
def step_impl(context):
    # fetch the endorser public DID and save in context
    endorser_config = call_endorser_service(context, GET, f"{ENDORSER_URL_PREFIX}/admin/config")
    assert "public_did" in endorser_config["endorser_config"], pprint.pp(endorser_config)

    # save for future reference
    endorser_did = endorser_config["endorser_config"]["public_did"]
    context.config.userdata["endorser_did"] = endorser_did


@given('there is a new author agent "{author}"')
def step_impl(context, author: str):
    # create (and authenticate) a new author agent
    if f"{author}_config" in context.config.userdata:
        del context.config.userdata[f"{author}_config"]

    rand_suffix = ("000000" + str(random.randint(1,100000)))[-6:]
    author_name = f"{author}_{rand_suffix}"
    data = {
        "key_management_mode": "managed",
        "label": author_name,
        "wallet_key": author_name,
        "wallet_name": author_name,
        "wallet_type": "indy",
    }

    author_wallet = call_agency_service(context, POST, "/multitenancy/wallet", data=data)
    assert "token" in author_wallet, pprint.pp(author_wallet)

    context.config.userdata[f"{author}_config"] = {
        "wallet": author_wallet,
    }

    # try calling the author wallet
    author_config = call_author_service(context, author, GET, "/status/config")
    assert "config" in author_config, pprint.pp(author_config)


@when('"{author}" connects to the endorser using their public DID')
def step_impl(context, author: str):
    # request a connection from the author to the endorser via public DID
    endorser_public_did = context.config.userdata["endorser_did"]["did"]
    endorser_alias = os.getenv("AUTHOR_ENDORSER_AlIAS")
    connection_request = call_author_service(
        context,
        author,
        POST,
        "/didexchange/create-request",
        params={
            "their_public_did": endorser_public_did,
            "alias": endorser_alias,
        },
    )
    assert "connection_id" in connection_request, pprint.pp(connection_request)

    # save the endorser connection request
    context.config.userdata[f"{author}_config"]["endorser_connection"] = connection_request


@when('the endorser accepts "{author}" connection request')
def step_impl(context, author: str):
    # find the connection request from "author"
    author_wallet = context.config.userdata[f"{author}_config"]["wallet"]
    author_alias = author_wallet["settings"]["default_label"]
    author_conn_request = None
    inc = 0
    while not author_conn_request:
        connection_requests = call_endorser_service(
            context,
            GET,
            f"{ENDORSER_URL_PREFIX}/connections",
            params={"state": "request"},
        )
        for connection in connection_requests["connections"]:
            if connection["their_label"] == author_alias:
                author_conn_request = connection
        if not author_conn_request:
            time.sleep(1)
            inc += 1
            assert inc < MAX_INC, f"Error too many retries can't find {author_alias}"

    # endorser accept the connection request

    # endorser set meta-data on the connection

    pass


@when('"{author}" sets endorser meta-data on the connection')
def step_impl(context, author: str):
    # author set meta-data on the connection

    pass


@then('"{author}" has an "{connection_status}" connection to the endorser')
def step_impl(context, author: str, connection_status: str):
    # verify the state of the author connection

    pass


@then('the endorser has an "{connection_status}" connection with "{author}"')
def step_impl(context, connection_status: str, author: str):
    # verify the state of the endorser connection

    pass
