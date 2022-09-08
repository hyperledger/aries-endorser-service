import json
import os
import pprint
import requests
import time

from behave import *
from starlette import status


ENDORSER_API_USER = os.getenv("ENDORSER_API_ADMIN_USER")
ENDORSER_API_PASSWORD = os.getenv("ENDORSER_API_ADMIN_KEY")
ENDORSER_BASE_URL = os.getenv("ENDORSER_SERVICE_BASE_URL")
ENDORSER_TOKEN_URL = ENDORSER_BASE_URL + "/endorser/token"

AGENCY_API_KEY = os.getenv("ACAPY_AUTHOR_API_ADMIN_KEY")
AGENCY_BASE_URL = os.getenv("ACAPY_AUTHOR_BASE_URL")

GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"
HEAD = "HEAD"
OPTIONS = "OPTIONS"

ENDORSER_URL_PREFIX = "/endorser/v1"
MAX_INC = 10
SLEEP_INC = 1


def endorser_headers(context) -> dict:
    if "endorser_auth_headers" in context.config.userdata:
        headers = context.config.userdata["endorser_auth_headers"]
    else:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
    return headers


def authenticate_endorser_service(context):
    """Authenticate against the endorser agent and save the token."""
    if "endorser_auth_headers" in context.config.userdata:
    	del context.config.userdata["endorser_auth_headers"]
    if "endorser_did" in context.config.userdata:
    	del context.config.userdata["endorser_did"]
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "username": ENDORSER_API_USER,
        "password": ENDORSER_API_PASSWORD,
        "grant_type": "",
        "scope": "",
    }
    response = requests.post(
        url=ENDORSER_TOKEN_URL,
        data=data,
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK, pprint.pp(response.__dict__)

    resp = json.loads(response.content)
    token = resp["access_token"]

    # save headers to context
    context.config.userdata["endorser_auth_headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    return context.config.userdata["endorser_auth_headers"]


def call_endorser_service(context, method, url_path, data=None, params=None, json_data=True):
    """Call an http service on the endorser agent."""
    endorser_url = ENDORSER_BASE_URL + url_path
    headers = endorser_headers(context)
    return call_http_service(method, endorser_url, headers, data=data, params=params, json_data=json_data)


def agency_headers(context) -> dict:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": AGENCY_API_KEY,
    }
    return headers


def call_agency_service(context, method, url_path, data=None, params=None, json_data=True):
    """Call an http service on the author agency (create author etc.)."""
    agency_url = AGENCY_BASE_URL + url_path
    headers = agency_headers(context)
    return call_http_service(method, agency_url, headers, data=data, params=params, json_data=json_data)


def author_headers(context, author_name) -> dict:
    if f"{author_name}_config" in context.config.userdata:
        token = context.config.userdata[f"{author_name}_config"]["wallet"]["token"]
    else:
        token = "n/a"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": AGENCY_API_KEY,
        "Authorization": f"Bearer {token}",
    }
    return headers


def call_author_service(context, author_name, method, url_path, data=None, params=None, json_data=True):
    """Call an http service on an author agent (within the agency)."""
    author_url = AGENCY_BASE_URL + url_path
    headers = author_headers(context, author_name)
    return call_http_service(method, author_url, headers, data=data, params=params, json_data=json_data)


def call_http_service(method, url, headers, data=None, params=None, json_data=True):
    method = method.upper()
    data = json.dumps(data) if data else None
    if method == POST:
        response = requests.post(
            url=url,
            data=data,
            headers=headers,
            params=params,
        )
    elif method == GET:
        response = requests.get(
            url=url,
            headers=headers,
            params=params,
        )
    elif method == PUT:
        response = requests.put(
            url=url,
            data=data,
            headers=headers,
            params=params,
        )
    elif method == DELETE:
        response = requests.delete(
            url=url,
            headers=headers,
            params=params,
        )
    elif method == HEAD:
        response = requests.head(
            url=url,
            headers=headers,
            params=params,
        )
    elif method == OPTIONS:
        response = requests.options(
            url=url,
            headers=headers,
            params=params,
        )
    else:
        assert False, f"Incorrect method passed: {method}"
    response.raise_for_status()
    if json_data:
        return response.json()
    else:
        return response.text


def set_endorser_config(context, config_name, config_value) -> dict:
    resp = call_endorser_service(
        context,
        POST,
        f"{ENDORSER_URL_PREFIX}/admin/config/{config_name}",
        params={"config_value": config_value}
    )
    return resp


def set_endorser_author_connection_config(context, author: str, author_status: str, endorse_status: str):
    author_wallet = get_author_context(context, author, "wallet")
    author_alias = author_wallet["settings"]["default_label"]
    connection = get_endorsers_author_connection(context, author_alias)
    connection_id = connection["connection_id"]
    params = {
        "author_status": author_status,
        "endorse_status": endorse_status,
    }
    connection = call_endorser_service(
        context,
        PUT,
        f"{ENDORSER_URL_PREFIX}/connections/{connection_id}/configure",
        params=params,
    )
    return connection


def set_endorser_author_connection_info(context, author: str, author_alias: str, public_did: str):
    author_wallet = get_author_context(context, author, "wallet")
    author_alias = author_wallet["settings"]["default_label"]
    connection = get_endorsers_author_connection(context, author_alias)
    connection_id = connection["connection_id"]
    params = {
        "alias": author_alias,
        "public_did": public_did,
    }
    connection = call_endorser_service(
        context,
        PUT,
        f"{ENDORSER_URL_PREFIX}/connections/{connection_id}",
        params=params,
    )
    return connection


def get_authors_endorser_connection(context, author: str, connection_id: str, connection_status: str=None):
    endorser_connection = None
    inc = 0
    while not endorser_connection:
        endorser_connection = call_author_service(
            context,
            author,
            GET,
            f"/connections/{connection_id}"
        )
        if (not endorser_connection) or (connection_status and not endorser_connection["state"] == connection_status):
            inc += 1
            assert inc <= MAX_INC, pprint.pp(endorser_connection)
            time.sleep(SLEEP_INC)

    if endorser_connection and connection_status:
        assert endorser_connection["state"] == connection_status, pprint.pp(endorser_connection)

    return endorser_connection


def get_endorsers_author_connection(context, author_alias: str, connection_status: str=None):
    author_conn_request = None
    params = {"page_size": 1000}
    if connection_status:
        params["state"] = connection_status
    inc = 0
    while not author_conn_request:
        connection_requests = call_endorser_service(
            context,
            GET,
            f"{ENDORSER_URL_PREFIX}/connections",
            params=params,
        )
        for connection in connection_requests["connections"]:
            if connection["their_label"] == author_alias:
                author_conn_request = connection
        if not author_conn_request:
            inc += 1
            assert inc <= MAX_INC, f"Error too many retries can't find {author_alias}"
            time.sleep(SLEEP_INC)

    if author_conn_request and connection_status:
        assert author_conn_request["state"] == connection_status, pprint.pp(author_conn_request)

    return author_conn_request


def get_endorser_transaction_record(context, connection_id: str, txn_state: str):
    endorser_txn = None
    inc = 0
    while not endorser_txn:
        # GET /v1/endorse/transactions with state request_received
        resp = call_endorser_service(
            context,
            GET,
            f"{ENDORSER_URL_PREFIX}/endorse/transactions",
            params={
                "transaction_state": txn_state,
                "connection_id": connection_id,
            },
        )
        if resp["count"] == 1:
            endorser_txn = resp["transactions"][0]
        else:
            inc += 1
            assert inc <= MAX_INC, f"Error too many retries can't find {connection_id} with {txn_state}"
            time.sleep(SLEEP_INC)

    assert endorser_txn, pprint.pp(endorser_txn)
    return endorser_txn


def get_author_transaction_record(context, author: str, transaction_id: str, txn_state: str = None):
    author_txn = None
    inc = 0
    while not author_txn:
        resp = call_author_service(
            context,
            author,
            GET,
            f"/transactions/{transaction_id}",
        )
        if (not resp) or (txn_state and not resp["state"] == txn_state):
            inc += 1
            assert inc <= MAX_INC, f"Error too many retries can't find {transaction_id} with {txn_state}"
            time.sleep(SLEEP_INC)
        else:
            author_txn = resp

    assert author_txn, pprint.pp(author_txn)
    return author_txn


def get_author_context(context, author: str, context_str: str):
    if (f"{author}_config" in context.config.userdata and 
        context_str in context.config.userdata[f"{author}_config"]):
        return context.config.userdata[f"{author}_config"][context_str]
    return None


def put_author_context(context, author: str, context_str: str, context_val):
    if not f"{author}_config" in context.config.userdata:
        context.config.userdata[f"{author}_config"] = {}
    context.config.userdata[f"{author}_config"][context_str] = context_val


def clear_author_context(context, author: str, context_str: str = None):
    if f"{author}_config" in context.config.userdata:
        if not context_str:
            del context.config.userdata[f"{author}_config"]
        elif context_str in context.config.userdata[f"{author}_config"]:
            del context.config.userdata[f"{author}_config"][context_str]


def get_endorser_context(context, context_str: str):
    return get_author_context(context, "endorser", context_str)


def put_endorser_context(context, context_str: str, context_val):
    put_author_context(context, "endorser", context_str, context_val)


def clear_endorser_context(context, context_str: str = None):
    clear_author_context(context, "endorser", context_str=context_str)
