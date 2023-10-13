import logging

from fastapi import APIRouter
from starlette import status


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", status_code=status.HTTP_200_OK, response_model=dict)
async def get_transaction_report() -> dict:
    # this should take some query params, sorting and paging params...
    return {}


@router.get(
    "/summary/{connection_id}", status_code=status.HTTP_200_OK, response_model=dict
)
async def get_connection_transaction_report(
    connection_id: str,
) -> dict:
    # this should take some query params, sorting and paging params...
    return {}
