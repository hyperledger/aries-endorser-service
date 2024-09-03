import os
import pprint
import random
import time
from typing import Literal

from behave import *
from requests import HTTPError
from util import (
    GET,
    POST,
    call_author_service,
    get_author_context,
    get_author_transaction_record,
    put_author_context,
    set_endorser_allowed_credential_definition,
    set_endorser_allowed_from_file,
    set_endorser_allowed_schema,
)

MAX_INC = 10
SLEEP_INC = 2
LEDGER_URL = os.getenv("LEDGER_URL")
REVOC_REG_COUNT = 5


@when('"{author}" creates a new schema')
def step_impl(context, author: str):
    # POST /schemas
    schema_name = "test_schema"
    schema_version = (
        str(random.randrange(100))
        + "."
        + str(random.randrange(100))
        + "."
        + str(random.randrange(100))
    )
    schema_attrs = [
        "full_name",
        "birthdate",
        "birthdate_dateint",
        "id_number",
        "favourite_colour",
    ]
    schema = {
        "schema_name": schema_name,
        "schema_version": schema_version,
        "attributes": schema_attrs,
    }
    resp = call_author_service(
        context,
        author,
        POST,
        "/schemas",
        data=schema,
    )
    assert "txn" in resp, pprint.pp(resp)
    assert "transaction_id" in resp["txn"], pprint.pp(resp)
    # save into context
    put_author_context(context, author, "current_transaction", resp["txn"])
    put_author_context(context, author, "current_schema", schema)


@when('the endorser allows "{author}" last schema')
@then('the endorser allows "{author}" last schema')
def step_impl(context, author: str):
    schema = get_author_context(context, author, "current_schema")
    resp = call_author_service(
        context,
        author,
        GET,
        "/wallet/did/public",
    )
    public_did = resp["result"]["did"]

    resp = set_endorser_allowed_schema(
        context,
        author_did=public_did,
        schema_name=schema["schema_name"],
        version=schema["schema_version"],
    )


from util import (
    AllowedCredentialDefinition,
    AllowedSchema,
)


@when('the endorser allows "{author}" last schema from file via "{POST_or_PUT}"')
@then('the endorser allows "{author}" last schema from file via "{POST_or_PUT}"')
def step_impl(context, author: str, POST_or_PUT: Literal["POST"] | Literal["PUT"]):
    schema = get_author_context(context, author, "current_schema")
    resp = call_author_service(
        context,
        author,
        GET,
        "/wallet/did/public",
    )
    public_did = resp["result"]["did"]

    resp = set_endorser_allowed_from_file(
        context,
        POST_or_PUT,
        schemas=[
            AllowedSchema(
                author_did=public_did,
                schema_name=schema["schema_name"],
                version=schema["schema_version"],
            )
        ],
    )
    print(resp)


@when("the endorser fails to allow duplicate schemas from file")
@then("the endorser fails to allow duplicate schemas from file")
def step_impl(context):
    try:
        set_endorser_allowed_from_file(
            context,
            POST,
            schemas=[
                AllowedSchema(
                    author_did="FwTnTZgfhjzVyDPEenT4cP",
                    schema_name="test_schema",
                    version="46.83.99",
                ),
                AllowedSchema(
                    author_did="FwTnTZgfhjzVyDPEenT4cP",
                    schema_name="test_schema",
                    version="46.83.99",
                ),
            ],
        )
        assert False
    except HTTPError as e:
        assert e.response.status_code == 409


@when('the endorser fails to allow "{author}" duplicate schemas')
@then('the endorser fails to allow "{author}" duplicate schemas')
def step_impl(context, author: str):
    try:
        schema = get_author_context(context, author, "current_schema")
        resp = call_author_service(
            context,
            author,
            GET,
            "/wallet/did/public",
        )
        public_did = resp["result"]["did"]
        resp = set_endorser_allowed_schema(
            context,
            author_did=public_did,
            schema_name=schema["schema_name"],
            version=schema["schema_version"],
        )
        assert False
    except HTTPError as e:
        assert e.response.status_code == 409


@when('"{author}" has an active schema on the ledger')
@then('"{author}" has an active schema on the ledger')
def step_impl(context, author: str):
    # GET /transactions/{tran_id}
    txn_request = get_author_context(context, author, "current_transaction")
    tnx_id = txn_request["transaction_id"]
    author_txn = get_author_transaction_record(
        context, author, tnx_id, "transaction_acked"
    )
    assert "meta_data" in author_txn, pprint.pp(author_txn)
    schema_id = author_txn["meta_data"]["context"]["schema_id"]

    # GET /schemas/created
    schemas_created = call_author_service(
        context,
        author,
        GET,
        "/schemas/created",
    )
    assert schema_id in schemas_created["schema_ids"], pprint.pp(schemas_created)

    # GET /schemas/{schema_id}
    schema_created = call_author_service(
        context,
        author,
        GET,
        f"/schemas/{schema_id}",
    )
    assert "schema" in schema_created, pprint.pp(schema_created)
    # save into context
    put_author_context(context, author, "current_schema", schema_created["schema"])


@when(
    '"{author}" creates a new credential definition "{with_or_without}" revocation support'
)
@then(
    '"{author}" creates a new credential definition "{with_or_without}" revocation support'
)
def step_impl(context, author: str, with_or_without: str):
    # POST /credential-definitions
    schema = get_author_context(context, author, "current_schema")
    schema_id = schema["id"]
    tag = "test_tag"
    cred_def = {
        "schema_id": schema_id,
        "tag": tag,
    }
    if with_or_without.lower() == "with":
        cred_def["support_revocation"] = True
        cred_def["revoc_reg_count"] = REVOC_REG_COUNT
    resp = call_author_service(
        context,
        author,
        POST,
        "/credential-definitions",
        data=cred_def,
    )
    assert "txn" in resp, pprint.pp(resp)
    assert "transaction_id" in resp["txn"], pprint.pp(resp)
    # save into context
    put_author_context(context, author, "current_transaction", resp["txn"])
    put_author_context(context, author, "current_cred_def", cred_def)


@then(
    'the endorser allows "{author}" last credential definition "{with_or_without}" revocation support'
)
@when(
    'the endorser allows "{author}" last credential definition "{with_or_without}" revocation support'
)
def step_impl(context, author: str, with_or_without: str):
    schema = get_author_context(context, author, "current_schema")
    cred_def = get_author_context(context, author, "current_cred_def")
    resp = call_author_service(
        context,
        author,
        GET,
        "/wallet/did/public",
    )
    public_did = resp["result"]["did"]

    schema_id = schema["id"].split(":")
    resp = set_endorser_allowed_credential_definition(
        context,
        tag=cred_def["tag"],
        rev_reg_def=with_or_without.lower() == "with",
        rev_reg_entry=with_or_without.lower() == "with",
        author_did=public_did,
        issuer_did=schema_id[0],
        schema_name=schema_id[2],
        version=schema_id[3],
    )


@then(
    'the endorser allows "{author}" last credential definition "{with_or_without}" revocation support from file via "{POST_or_PUT}"'
)
@when(
    'the endorser allows "{author}" last credential definition "{with_or_without}" revocation support from file via "{POST_or_PUT}"'
)
def step_impl(
    context,
    author: str,
    with_or_without: str,
    POST_or_PUT: Literal["POST"] | Literal["PUT"],
):
    schema = get_author_context(context, author, "current_schema")
    cred_def = get_author_context(context, author, "current_cred_def")
    resp = call_author_service(
        context,
        author,
        GET,
        "/wallet/did/public",
    )
    public_did = resp["result"]["did"]

    schema_id = schema["id"].split(":")
    resp = set_endorser_allowed_from_file(
        context,
        POST_or_PUT,
        credential_definition=[
            AllowedCredentialDefinition(
                tag=cred_def["tag"],
                rev_reg_def=with_or_without.lower() == "with",
                rev_reg_entry=with_or_without.lower() == "with",
                author_did=public_did,
                issuer_did=schema_id[0],
                schema_name=schema_id[2],
                version=schema_id[3],
            )
        ],
    )
    print(resp)


@when('"{author}" has an active credential definition on the ledger')
@then('"{author}" has an active credential definition on the ledger')
def step_impl(context, author: str):
    # GET /transactions/{tran_id}
    txn_request = get_author_context(context, author, "current_transaction")
    tnx_id = txn_request["transaction_id"]
    author_txn = get_author_transaction_record(
        context, author, tnx_id, "transaction_acked"
    )
    assert "meta_data" in author_txn, pprint.pp(author_txn)
    cred_def_id = author_txn["meta_data"]["context"]["cred_def_id"]

    # GET /credential-definitions/created
    cred_defs_created = call_author_service(
        context,
        author,
        GET,
        "/credential-definitions/created",
    )
    assert cred_def_id in cred_defs_created["credential_definition_ids"], pprint.pp(
        cred_defs_created
    )

    # GET /credential-definitions/{cred_def_id}
    cred_def_created = call_author_service(
        context,
        author,
        GET,
        f"/credential-definitions/{cred_def_id}",
    )
    assert "credential_definition" in cred_def_created, pprint.pp(cred_def_created)
    # save into context
    put_author_context(
        context,
        author,
        "current_credential_definition",
        cred_def_created["credential_definition"],
    )


@then('"{author}" has an active revocation registry on the ledger')
def step_impl(context, author: str):
    cred_def = get_author_context(context, author, "current_credential_definition")
    cred_def_id = cred_def["id"]
    active_rev_reg = None
    inc = 0
    while not active_rev_reg:
        # GET /revocation/active-registry/{cred_def_id}
        try:
            resp = call_author_service(
                context,
                author,
                GET,
                f"/revocation/active-registry/{cred_def_id}",
            )
            if "result" in resp and resp["result"]:
                active_rev_reg = resp["result"]
        except HTTPError:
            pass

        if not active_rev_reg:
            inc += 1
            assert inc <= MAX_INC, pprint.pp(
                "Error too many retries can't find " + str(cred_def_id)
            )
            time.sleep(SLEEP_INC)
