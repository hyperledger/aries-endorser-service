from enum import Enum
import json
import logging

from pydantic import BaseModel

from api.db.models.endorse_request import EndorseRequest


logger = logging.getLogger(__name__)


class EndorserRoleType(str, Enum):
    Author = "TRANSACTION_AUTHOR"
    Endorser = "TRANSACTION_ENDORSER"


class EndorseTransactionState(str, Enum):
    transaction_created = "transaction_created"
    request_sent = "request_sent"
    request_received = "request_received"
    transaction_endorsed = "transaction_endorsed"
    transaction_refused = "transaction_refused"
    transaction_resent = "transaction_resent"
    transaction_resent_received = "transaction_resent_received"
    transaction_cancelled = "transaction_cancelled"
    transaction_acked = "transaction_acked"


class EndorseTransactionType(str, Enum):
    did = "1"
    attrib = "100"
    schema = "101"
    cred_def = "102"
    revoc_registry = "113"
    revoc_entry = "114"


class EndorseTransaction(BaseModel):
    author_goal_code: str | None
    connection_id: str
    transaction_id: str
    tags: list[str]
    created_at: str | None = None
    state: str
    transaction_request: dict
    endorser_did: str
    author_did: str | None = None
    transaction: dict | None = None
    transaction_type: str | None = None
    transaction_response: dict | None = None


class EndorseTransactionList(BaseModel):
    page_size: int
    page_num: int
    count: int
    total_count: int
    transactions: list[EndorseTransaction]


def webhook_to_txn_object(payload: dict, endorser_did: str) -> EndorseTransaction:
    """Convert from a webhook payload to an endorser transaction."""
    logger.debug(f">>> from payload: {payload}")
    if (
        "json" in payload["messages_attach"][0]["data"]
        and payload["messages_attach"][0]["data"]["json"]
    ):
        # deal with str or dict types
        payload_json = payload["messages_attach"][0]["data"]["json"]
        if isinstance(payload_json, dict):
            transaction_request = payload_json
        else:
            transaction_request = json.loads(payload_json)
    else:
        transaction_request = {}
    if 0 < len(payload["signature_response"]):
        transaction_response = (
            json.loads(payload["signature_response"][0]["signature"][endorser_did])
            if payload["signature_response"][0]["signature"][endorser_did]
            else None
        )
    else:
        transaction_response = {}
    transaction: EndorseTransaction = EndorseTransaction(
        author_goal_code=payload.get("signature_request")[0].get("author_goal_code"),
        connection_id=payload.get("connection_id"),
        transaction_id=payload.get("transaction_id"),
        tags=[],
        state=payload.get("state"),
        transaction_request=transaction_request,
        endorser_did=endorser_did,
        author_did=transaction_request["identifier"]
        if transaction_request and "identifier" in transaction_request
        else None,
        transaction=transaction_request["operation"]
        if transaction_request and "operation" in transaction_request
        else None,
        transaction_type=transaction_request["operation"]["type"]
        if transaction_request and "operation" in transaction_request
        else None,
        transaction_response=transaction_response,
    )
    logger.debug(f">>> to transaction: {transaction}")
    return transaction


def txn_to_db_object(txn: EndorseTransaction) -> EndorseRequest:
    """Convert from model object to database model object."""
    logger.debug(f">>> from transaction: {txn}")
    txn_request: EndorseRequest = EndorseRequest(
        author_goal_code=txn.author_goal_code,
        transaction_id=txn.transaction_id,
        connection_id=txn.connection_id,
        tags=txn.tags,
        endorser_did=txn.endorser_did,
        author_did=txn.author_did,
        transaction_type=txn.transaction_type,
        state=txn.state,
        # TODO extract transaction_request into it's own field
        ledger_txn=json.dumps(txn.transaction)
        if txn.transaction
        else json.dumps(txn.transaction_request),
    )
    logger.debug(f">>> to request: {txn_request}")
    return txn_request


def db_to_txn_object(
    txn_request: EndorseRequest, acapy_txn: dict | None = None
) -> EndorseTransaction:
    """Convert from database and acapy objects to model object."""
    if acapy_txn:
        transaction_request = json.loads(
            acapy_txn["messages_attach"][0]["data"]["json"]
        )
        transaction = transaction_request.get("operation")
        if 0 < len(acapy_txn["signature_response"]):
            transaction_response = json.loads(
                acapy_txn["signature_response"][0]["signature"][
                    txn_request.endorser_did
                ]
            )
        else:
            transaction_response = {}
    else:
        transaction_request = {}
        transaction_response = {}
        # transaction = {}
    logger.debug(
        f"contents of the ledger_txn for {str(txn_request.transaction_id)} is {txn_request.ledger_txn}"
    )
    txn: EndorseTransaction = EndorseTransaction(
        author_goal_code=str(txn_request.author_goal_code),
        connection_id=str(txn_request.connection_id),
        transaction_id=str(txn_request.transaction_id),
        tags=txn_request.tags,
        state=acapy_txn.get("state") if acapy_txn else txn_request.state,
        transaction_request=transaction_request,
        endorser_did=txn_request.endorser_did,
        author_did=txn_request.author_did,
        transaction=json.loads(txn_request.ledger_txn),
        transaction_type=txn_request.transaction_type,
        transaction_response=transaction_response,
    )
    return txn
