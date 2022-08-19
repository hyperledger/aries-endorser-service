import json
import time
import pprint
import random

from behave import *
from starlette import status

from util import (
	authenticate_endorser_service,
	call_endorser_service,
	call_agency_service,
	call_author_service,
)


GET = "GET"
POST = "POST"
PUT = "PUT"

ENDORSER_URL_PREFIX = "/endorser/v1"


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
		"label": author,
		"wallet_key": author_name,
		"wallet_name": author_name,
		"wallet_type": "indy",
	}

	author_wallet = call_agency_service(context, POST, "/multitenancy/wallet", data=data)
	assert "token" in author_wallet, pprint.pp(author_wallet)

	context.config.userdata[f"{author}_config"] = author_wallet


@when('"{author}" connects to the endorser using their public DID')
def step_impl(context, author: str):
	# request a connection from the author to the endorser via public DID

	pass


@when('the endorser accepts "{author}" connection request')
def step_impl(context, author: str):
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
