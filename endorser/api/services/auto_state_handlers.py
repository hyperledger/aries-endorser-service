import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.endpoints.models.endorse import (
    EndorseTransaction,
    webhook_to_txn_object,
)
from api.endpoints.models.connections import (
    webhook_to_connection_object,
)
from api.services.connections import (
    store_connection_request,
    update_connection_status,
    accept_connection_request,
)
from api.services.configurations import (
    get_bool_config,
)
from api.services.endorse import (
    endorse_transaction,
    get_endorser_did,
)


logger = logging.getLogger(__name__)


def is_auto_endorse_connection(transaction: EndorseTransaction) -> bool:
    # TODO check if connection or author_did is setup for auto-endorse
    return False


async def auto_step_ping_received(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    return {}


async def auto_step_connections_request(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # auto-accept connection?
    connection: Connection = webhook_to_connection_object(payload)
    if await get_bool_config(db, "ENDORSER_AUTO_ACCEPT_CONNECTIONS"):
        result = await accept_connection_request(db, connection)
    return {}


async def auto_step_connections_response(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # no-op
    return {}


async def auto_step_connections_active(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # no-op
    return {}


async def auto_step_connections_completed(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # no-op
    return {}


async def auto_step_endorse_transaction_request_received(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # TODO check if auto-endorse for this connection
    logger.info(">>> in auto_step_endorse_transaction_request_received() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    logger.debug(f">>> transaction = {transaction}")
    result = {}
    if await get_bool_config(db, "ENDORSER_AUTO_ENDORSE_REQUESTS") or is_auto_endorse_connection(transaction):
        result = await endorse_transaction(db, transaction)
    return result


async def auto_step_endorse_transaction_transaction_endorsed(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    logger.info(">>> in auto_step_endorse_transaction_transaction_endorsed() ...")
    return {}


async def auto_step_endorse_transaction_transaction_acked(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    logger.info(">>> in auto_step_endorse_transaction_transaction_acked() ...")
    return {}
