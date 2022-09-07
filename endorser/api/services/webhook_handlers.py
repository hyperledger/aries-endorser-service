import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.models.connections import ConnectionProtocolType
from api.endpoints.models.connections import (
    Connection,
    webhook_to_connection_object,
)
from api.endpoints.models.endorse import (
    EndorserRoleType,
    EndorseTransaction,
    webhook_to_txn_object,
)
from api.services.connections import (
    store_connection_request,
    update_connection_status,
    set_connection_author_metadata,
)
from api.services.endorse import (
    store_endorser_request,
    update_endorsement_status,
    get_endorser_did,
)

import api.acapy_utils as au


logger = logging.getLogger(__name__)


async def handle_ping_received(db: AsyncSession, payload: dict) -> dict:
    logger.info(">>> in handle_ping_received() ...")
    return {}


async def handle_connections_request(db: AsyncSession, payload: dict):
    """Handle transaction endorse requests."""
    logger.info(">>> in handle_connections_request() ...")
    connection: Connection = webhook_to_connection_object(payload)
    result = await store_connection_request(db, connection)
    return result


async def handle_connections_response(db: AsyncSession, payload: dict):
    connection: Connection = webhook_to_connection_object(payload)
    result = await update_connection_status(db, connection)
    return result


async def handle_connections_active(db: AsyncSession, payload: dict):
    connection: Connection = webhook_to_connection_object(payload)
    result = await update_connection_status(db, connection)
    return result


async def handle_connections_completed(db: AsyncSession, payload: dict):
    """Set endorser role on any connections we receive."""
    # TODO check final state for other connections protocols
    if payload["connection_protocol"] == ConnectionProtocolType.DIDExchange.value:
        connection: Connection = webhook_to_connection_object(payload)
        await set_connection_author_metadata(db, connection)
    return {}


async def handle_endorse_transaction_request_received(db: AsyncSession, payload: dict):
    """Handle transaction endorse requests."""
    logger.info(">>> in handle_endorse_transaction_request_received() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    result = await store_endorser_request(db, transaction)
    return result


async def handle_endorse_transaction_transaction_endorsed(
    db: AsyncSession, payload: dict
):
    logger.info(">>> in handle_endorse_transaction_transaction_endorsed() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    result = await update_endorsement_status(db, transaction)
    return result


async def handle_endorse_transaction_transaction_refused(
    db: AsyncSession, payload: dict
):
    logger.info(">>> in handle_endorse_transaction_transaction_refused() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    result = await update_endorsement_status(db, transaction)
    return result


async def handle_endorse_transaction_transaction_acked(db: AsyncSession, payload: dict):
    logger.info(">>> in handle_endorse_transaction_transaction_acked() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    result = await update_endorsement_status(db, transaction)
    return result
