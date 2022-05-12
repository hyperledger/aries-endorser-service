import logging
from typing import List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.endorse import (
    EndorseTransaction,
    EndorseTransactionList,
)
from api.services.endorse import (
    get_transactions_list,
    get_transaction_object,
    endorse_transaction,
    reject_transaction,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/transactions",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransactionList,
)
async def get_transactions(
    transaction_state: Optional[str] = None,
    connection_id: Optional[str] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransactionList:
    # this should take some query params, sorting and paging params...
    (total_count, transactions) = await get_transactions_list(
        db,
        transaction_state=transaction_state,
        connection_id=connection_id,
        page_size=page_size,
        page_num=page_num,
    )
    response: EndorseTransactionList = EndorseTransactionList(
        page_size=page_size,
        page_num=page_num,
        count=len(transactions),
        total_count=total_count,
        transactions=transactions,
    )
    return response


@router.get(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransaction,
)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransaction:
    transaction = await get_transaction_object(db, transaction_id)
    return transaction


@router.put(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransaction,
)
async def update_transactions(
    transaction_id: str,
    meta_data: dict,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransaction:
    """Update meta-data (tags) on a transaction."""
    return None


@router.post(
    "/transactions/{transaction_id}/endorse",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransaction,
)
async def endorse_transaction_endpoint(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransaction:
    """Manually approve an endorsement."""
    transaction: EndorseTransaction = await get_transaction_object(db, transaction_id)
    endorsed_txn = await endorse_transaction(db, transaction)
    return endorsed_txn


@router.post(
    "/transactions/{transaction_id}/reject",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransaction,
)
async def reject_transaction_endpoint(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransaction:
    """Manually reject an endorsement."""
    transaction: EndorseTransaction = await get_transaction_object(db, transaction_id)
    rejected_txn = await reject_transaction(db, transaction)
    return rejected_txn
