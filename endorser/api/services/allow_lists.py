import logging
from typing import TypeVar
from api.db.models.base import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from psycopg2.errors import UniqueViolation
from api.endpoints.models.endorse import (
    EndorseTransactionState,
    db_to_txn_object,
)
from api.db.models.endorse_request import EndorseRequest
from api.services.auto_state_handlers import is_endorsable_transaction
from api.services.endorse import endorse_transaction
from api.db.errors import AlreadyExists


logger = logging.getLogger(__name__)


async def updated_allowed(db: AsyncSession) -> None:
    try:
        q = select(EndorseRequest).where(
            EndorseRequest.state == EndorseTransactionState.request_received
        )
        result = await db.execute(q)
        db_txns: list[EndorseRequest] = result.scalars().all()
        for txn in db_txns:
            transaction = db_to_txn_object(txn, acapy_txn=None)
            logger.debug(
                f">>> from updated_allowed: the current transaction is {transaction}"
            )
            was_allowed = await is_endorsable_transaction(db, transaction)
            logger.debug(f">>> from updated_allowed: this was allowed? {was_allowed}")
            if was_allowed:
                logger.debug(
                    f">>> from updated_allowed: endorsing transaction: {transaction}"
                )
                await endorse_transaction(db, transaction)
    except Exception as e:
        # try to retrieve and print text on error
        logger.error(f"Failed to update pending transactions {e}")


B = TypeVar("B", bound=BaseModel)


async def add_to_allow_list(db: AsyncSession, a: B) -> B:
    try:
        db.add(a)
        await db.commit()
        await updated_allowed(db)
        return a
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise AlreadyExists(f"{a} already exists")
        else:
            raise e
