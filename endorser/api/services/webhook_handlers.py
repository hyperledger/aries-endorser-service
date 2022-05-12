import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.models.connections import ConnectionProtocolType
from api.endpoints.models.endorse import (
    EndorserRoleType,
    EndorseTransaction,
    webhook_to_txn_object,
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


async def handle_connections_completed(db: AsyncSession, payload: dict):
    """Set endorser role on any connections we receive."""
    # TODO check final state for other connections protocols
    if payload["connection_protocol"] == ConnectionProtocolType.DIDExchange.value:
        # confirm if we have already set the role on this connection
        connection_id = payload["connection_id"]
        logger.info(f">>> check for metadata on connection: {connection_id}")
        conn_meta_data = await au.acapy_GET(f"connections/{connection_id}/metadata")
        if "transaction-jobs" in conn_meta_data["results"]:
            if "transaction_my_job" in conn_meta_data["results"]["transaction-jobs"]:
                return

        # set our endorser role
        params = {"transaction_my_job": EndorserRoleType.Endorser.value}
        logger.info(
            f">>> Setting meta-data for connection: {payload}, with params: {params}"
        )
        await au.acapy_POST(
            f"transactions/{connection_id}/set-endorser-role", params=params
        )
    return {}


async def handle_endorse_transaction_request_received(db: AsyncSession, payload: dict):
    """Handle transaction endorse requests."""
    # TODO log the endorsement request
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


async def handle_endorse_transaction_transaction_acked(db: AsyncSession, payload: dict):
    logger.info(">>> in handle_endorse_transaction_transaction_acked() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    result = await update_endorsement_status(db, transaction)
    return result
