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
    response_model=List[dict],
)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # this should take some query params, sorting and paging params...
    return None


@router.put(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[dict],
)
async def update_transactions(
    transaction_id: str,
    meta_data: dict,
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    # this should take some query params, sorting and paging params...
    return None


@router.post(
    "/transactions/{transaction_id}/endorse",
    status_code=status.HTTP_200_OK,
    response_model=List[dict],
)
async def endorse_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # this should take some query params, sorting and paging params...
    return None


@router.post(
    "/transactions/{transaction_id}/reject",
    status_code=status.HTTP_200_OK,
    response_model=List[dict],
)
async def reject_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # this should take some query params, sorting and paging params...
    return None
