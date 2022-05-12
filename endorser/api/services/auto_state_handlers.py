import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.endpoints.models.endorse import (
    EndorseTransaction,
    webhook_to_txn_object,
)
from api.services.endorse import (
    endorse_transaction,
    get_endorser_did,
)


logger = logging.getLogger(__name__)


def auto_endorse_connection(transaction: EndorseTransaction) -> bool:
    # TODO check if connection is setup for auto-endorse
    return True


async def auto_step_endorse_transaction_request_received(
    db: AsyncSession, payload: dict, handler_result: dict
):
    # TODO check if auto-endorse for this connection
    logger.info(">>> in auto_step_endorse_transaction_request_received() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    logger.debug(f">>> transaction = {transaction}")
    if settings.ENDORSER_AUTO_ENDORSE_REQUESTS or auto_endorse_connection(transaction):
        result = await endorse_transaction(db, transaction)
    return result


async def auto_step_endorse_transaction_transaction_endorsed(
    db: AsyncSession, payload: dict, handler_result: dict
):
    logger.info(">>> in auto_step_endorse_transaction_transaction_endorsed() ...")
    return {}


async def auto_step_endorse_transaction_transaction_acked(
    db: AsyncSession, payload: dict, handler_result: dict
):
    logger.info(">>> in auto_step_endorse_transaction_transaction_acked() ...")
    return {}
