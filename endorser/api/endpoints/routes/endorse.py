import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.endorse import (
    EndorseTransaction,
    EndorseTransactionList,
    EndorseTransactionState,
)
from api.services.endorse import (
    get_transactions_list,
    get_transaction_object,
    endorse_transaction,
    reject_transaction,
)
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/transactions",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransactionList,
)
async def get_transactions(
    transaction_state: Optional[EndorseTransactionState] = None,
    connection_id: Optional[str] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransactionList:
    try:
        (total_count, transactions) = await get_transactions_list(
            db,
            transaction_state=transaction_state.value if transaction_state else None,
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
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransaction,
)
async def get_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransaction:
    try:
        transaction = await get_transaction_object(db, transaction_id)
        return transaction
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    raise NotImplementedError


@router.post(
    "/transactions/{transaction_id}/endorse",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransaction,
)
async def endorse_transaction_endpoint(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransaction:
    """Manually approve an endorsement."""
    try:
        transaction: EndorseTransaction = await get_transaction_object(
            db, transaction_id
        )
        endorsed_txn = await endorse_transaction(db, transaction)
        return endorsed_txn
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/transactions/{transaction_id}/reject",
    status_code=status.HTTP_200_OK,
    response_model=EndorseTransaction,
)
async def reject_transaction_endpoint(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EndorseTransaction:
    """Manually reject an endorsement."""
    try:
        transaction: EndorseTransaction = await get_transaction_object(
            db, transaction_id
        )
        rejected_txn = await reject_transaction(db, transaction)
        return rejected_txn
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
