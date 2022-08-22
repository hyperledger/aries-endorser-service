import json
import os
import pprint
import requests

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
