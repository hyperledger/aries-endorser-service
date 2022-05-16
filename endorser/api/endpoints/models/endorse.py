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
    schema = "101"
    cred_def = "102"
    revoc_registry = "113"
    revoc_entry = "114"


class EndorseTransaction(BaseModel):
    connection_id: str
    transaction_id: str
    tags: list[str]
    created_at: str | None = None
    state: str
    transaction_request: dict
    endorser_did: str
    author_did: str
    transaction: dict
    transaction_type: str
    transaction_response: dict


class EndorseTransactionList(BaseModel):
    page_size: int
    page_num: int
    count: int
    total_count: int
    transactions: list[EndorseTransaction]


def webhook_to_txn_object(payload: dict, endorser_did: str) -> EndorseTransaction:
    """Convert from a webhook payload to an endorser transaction."""
    logger.debug(f">>> from payload: {payload}")
    transaction_request = json.loads(payload["messages_attach"][0]["data"]["json"])
    if 0 < len(payload["signature_response"]):
        transaction_response = json.loads(
            payload["signature_response"][0]["signature"][endorser_did]
        )
    else:
        transaction_response = {}
    transaction: EndorseTransaction = EndorseTransaction(
        connection_id=payload.get("connection_id"),
        transaction_id=payload.get("transaction_id"),
        tags=[],
        state=payload.get("state"),
        transaction_request=transaction_request,
        endorser_did=endorser_did,
        author_did=transaction_request["identifier"],
        transaction=transaction_request["operation"],
        transaction_type=transaction_request["operation"]["type"],
        transaction_response=transaction_response,
    )
    logger.debug(f">>> to transaction: {transaction}")
    return transaction


def txn_to_db_object(txn: EndorseTransaction) -> EndorseRequest:
    """Convert from model object to database model object."""
    logger.debug(f">>> from transaction: {txn}")
    txn_request: EndorseRequest = EndorseRequest(
        transaction_id=txn.transaction_id,
        connection_id=txn.connection_id,
        tags=txn.tags,
        endorser_did=txn.endorser_did,
        author_did=txn.author_did,
        transaction_type=txn.transaction_type,
        state=txn.state,
        ledger_txn=json.dumps(txn.transaction),
    )
    logger.debug(f">>> to request: {txn_request}")
    return txn_request


def db_to_txn_object(
    txn_request: EndorseRequest, acapy_txn: dict = None
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
        transaction = {}
    txn: EndorseTransaction = EndorseTransaction(
        connection_id=str(txn_request.connection_id),
        transaction_id=str(txn_request.transaction_id),
        tags=txn_request.tags,
        state=acapy_txn.get("state") if acapy_txn else txn_request.state,
        transaction_request=transaction_request,
        endorser_did=txn_request.endorser_did,
        author_did=txn_request.author_did,
        transaction=transaction,
        transaction_type=txn_request.transaction_type,
        transaction_response=transaction_response,
    )
    return txn
