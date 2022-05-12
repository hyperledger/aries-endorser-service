import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from api.core.config import settings
from api.endpoints.models.endorse import EndorseTransactionState, EndorseTransaction, txn_to_db_object
from api.db.models.endorse_request import EndorseRequest
from api.db.errors import DoesNotExist

import api.acapy_utils as au


logger = logging.getLogger(__name__)


async def get_endorser_did() -> str:
    diddoc = await au.acapy_GET("wallet/did/public")
    did = diddoc["result"]["did"]
    logger.info(f">>> returning diddoc: {did}")
    return did


async def store_endorser_request(db: AsyncSession, txn: EndorseTransaction):
    logger.info(f">>> called store_endorser_request with: {txn}")
    db_txn: EndorseRequest = txn_to_db_object(txn)
    db.add(db_txn)
    await db.commit()
    logger.info(">>> stored endorser_request")
    return txn


async def endorse_transaction(db: AsyncSession, txn: EndorseTransaction):
    logger.info(f">>> called endorse_transaction with: {txn}")
    # fetch existing db object
    q = (
        select(EndorseRequest)
        .where(EndorseRequest.transaction_id == txn.transaction_id)
    )
    result = await db.execute(q)
    result_rec = result.scalar_one_or_none()
    if not result_rec:
        raise DoesNotExist(
            f"{EndorseRequest.__name__}<transaction_id:{txn.transaction_id}> does not exist"
        )
    db_txn: EndorseRequest = EndorseRequest.from_orm(result_rec)

    # endorse transaction and tell aca-py
    # TODO

    # update local db status
    payload_dict = db_txn.dict()
    q = (
        update(EndorseRequest)
        .where(EndorseRequest.endorse_request_id == db_txn.endorse_request_id)
        .where(EndorseRequest.transaction_id == txn.transaction_id)
        .values(payload_dict)
    )
    await db.execute(q)
    await db.commit()
    logger.info(">>> updated endorser_request")
    return txn


async def update_endorsement_status(db: AsyncSession, txn: EndorseTransaction):
    logger.info(f">>> called update_endorsement_status with: {txn}")
    # fetch existing db object
    q = (
        select(EndorseRequest)
        .where(EndorseRequest.transaction_id == txn.transaction_id)
    )
    result = await db.execute(q)
    result_rec = result.scalar_one_or_none()
    if not result_rec:
        raise DoesNotExist(
            f"{EndorseRequest.__name__}<transaction_id:{txn.transaction_id}> does not exist"
        )
    db_txn: EndorseRequest = EndorseRequest.from_orm(result_rec)

    # update state from webhook

    # update local db status
    payload_dict = db_txn.dict()
    q = (
        update(EndorseRequest)
        .where(EndorseRequest.endorse_request_id == db_txn.endorse_request_id)
        .where(EndorseRequest.transaction_id == txn.transaction_id)
        .values(payload_dict)
    )
    await db.execute(q)
    await db.commit()
    logger.info(">>> updated endorser_request")
    return txn
