import logging
from typing import List, Optional
import json

from fastapi import APIRouter
from starlette import status

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/transactions", status_code=status.HTTP_200_OK, response_model=List[dict])
async def get_transactions(
    transaction_state: Optional[str] = None,
) -> List[dict]:
    # this should take some query params, sorting and paging params...
    return [{}]


@router.get("/transactions/{transaction_id}", status_code=status.HTTP_200_OK, response_model=List[dict])
async def get_transaction(
    transaction_id: str,
) -> dict:
    # this should take some query params, sorting and paging params...
    return None


@router.put("/transactions/{transaction_id}", status_code=status.HTTP_200_OK, response_model=List[dict])
async def update_transactions(
    transaction_id: str,
    meta_data: dict,
) -> List[dict]:
    # this should take some query params, sorting and paging params...
    return None


@router.post("/transactions/{transaction_id}/endorse", status_code=status.HTTP_200_OK, response_model=List[dict])
async def endorse_transaction(
    transaction_id: str,
) -> dict:
    # this should take some query params, sorting and paging params...
    return None


@router.post("/transactions/{transaction_id}/reject", status_code=status.HTTP_200_OK, response_model=List[dict])
async def reject_transaction(
    transaction_id: str,
) -> dict:
    # this should take some query params, sorting and paging params...
    return None
