import logging
from typing import cast
from uuid import UUID

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

import api.acapy_utils as au
from api.db.errors import DoesNotExist
from api.db.models.endorse_request import EndorseRequest
from api.endpoints.models.endorse import (
    EndorseTransaction,
    db_to_txn_object,
    txn_to_db_object,
)

logger = logging.getLogger(__name__)


async def get_endorser_did() -> str:
    diddoc = cast(dict, await au.acapy_GET("wallet/did/public"))
    did = cast(str, diddoc["result"]["did"])
    return did


async def db_add_db_txn_record(db: AsyncSession, db_txn: EndorseRequest):
    db.add(db_txn)
    await db.commit()


async def db_fetch_db_txn_record(
    db: AsyncSession, transaction_id: UUID
) -> EndorseRequest:
    logger.info(f">>> db_fetch_db_txn_record() for {transaction_id}")
    q = select(EndorseRequest).where(EndorseRequest.transaction_id == transaction_id)
    result = await db.execute(q)
    result_rec = result.scalar_one_or_none()
    if not result_rec:
        raise DoesNotExist(
            f"{EndorseRequest.__name__}<transaction_id:{transaction_id}> does not exist"
        )
    return result_rec


async def db_update_db_txn_record(
    db: AsyncSession, db_txn: EndorseRequest
) -> EndorseRequest:
    payload_dict = db_txn.dict()
    q = (
        update(EndorseRequest)
        .where(EndorseRequest.endorse_request_id == db_txn.endorse_request_id)
        .where(EndorseRequest.transaction_id == db_txn.transaction_id)
        .values(payload_dict)
    )
    await db.execute(q)
    await db.commit()
    return await db_fetch_db_txn_record(db, db_txn.transaction_id)


async def db_get_txn_records(
    db: AsyncSession,
    state: str | None = None,
    connection_id: str | None = None,
    page_size: int = 10,
    page_num: int = 1,
) -> tuple[int, list[EndorseRequest]]:
    limit = page_size
    skip = (page_num - 1) * limit
    filters = []
    if state:
        filters.append(EndorseRequest.state == state)
    if connection_id:
        filters.append(EndorseRequest.connection_id == connection_id)

    # build out a base query with all filters
    base_q = select(EndorseRequest).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = base_q.with_only_columns(func.count()).order_by(None)
    count_q_rec = await db.execute(count_q)
    total_count: int = count_q_rec.scalar() or 0

    # add in our paging and ordering to get the result set
    results_q = (
        base_q.limit(limit).offset(skip).order_by(desc(EndorseRequest.created_at))
    )

    results_q_recs = await db.execute(results_q)
    db_txns: list[EndorseRequest] = results_q_recs.scalars().all()

    return (total_count, db_txns)


async def get_transactions_list(
    db: AsyncSession,
    transaction_state: str | None = None,
    connection_id: str | None = None,
    page_size: int = 10,
    page_num: int = 1,
) -> tuple[int, list[EndorseTransaction]]:
    (count, db_txns) = await db_get_txn_records(
        db,
        state=transaction_state,
        connection_id=connection_id,
        page_size=page_size,
        page_num=page_num,
    )
    items = []
    for db_txn in db_txns:
        item = db_to_txn_object(db_txn, acapy_txn=None)
        items.append(item)
    return (count, items)


async def get_transaction_object(
    db: AsyncSession,
    transaction_id: UUID,
) -> EndorseTransaction:
    logger.info(f">>> get_transaction_object() for {transaction_id}")
    db_txn: EndorseRequest = await db_fetch_db_txn_record(db, transaction_id)
    item = db_to_txn_object(db_txn, acapy_txn=None)
    return item


async def store_endorser_request(db: AsyncSession, txn: EndorseTransaction):
    logger.info(f">>> called store_endorser_request with: {txn.transaction_id}")

    db_txn: EndorseRequest = txn_to_db_object(txn)
    await db_add_db_txn_record(db, db_txn)
    logger.info(f">>> stored endorser_request: {db_txn.transaction_id}")

    return txn


async def endorse_transaction(db: AsyncSession, txn: EndorseTransaction):
    logger.info(f">>> called endorse_transaction with: {txn.transaction_id}")

    # fetch existing db object
    db_txn: EndorseRequest = await db_fetch_db_txn_record(db, txn.transaction_id)

    # endorse transaction and tell aca-py
    response = cast(
        dict, await au.acapy_POST(f"transactions/{txn.transaction_id}/endorse")
    )

    # update local db state
    db_txn.state = response["state"]
    db_txn = await db_update_db_txn_record(db, db_txn)
    logger.info(f">>> endorsed endorser_request for {txn.transaction_id}")

    return txn


async def reject_transaction(db: AsyncSession, txn: EndorseTransaction):
    logger.info(f">>> called reject_transaction with: {txn.transaction_id}")

    # fetch existing db object
    db_txn: EndorseRequest = await db_fetch_db_txn_record(db, txn.transaction_id)

    # endorse transaction and tell aca-py
    response = cast(
        dict, await au.acapy_POST(f"transactions/{txn.transaction_id}/refuse")
    )

    # update local db state
    db_txn.state = response["state"]
    db_txn = await db_update_db_txn_record(db, db_txn)
    logger.info(f">>> rejected endorser_request for {txn.transaction_id}")

    return txn


async def update_endorsement_status(db: AsyncSession, txn: EndorseTransaction):
    logger.info(f">>> called update_endorsement_status with: {txn.transaction_id}")

    # fetch existing db object
    db_txn: EndorseRequest = await db_fetch_db_txn_record(db, txn.transaction_id)

    # update local db state
    db_txn.state = txn.state
    db_txn = await db_update_db_txn_record(db, db_txn)
    logger.info(f">>> updated endorser_request for {txn.transaction_id} {txn.state}")

    return txn
