import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.connections import (
    ConnectionStateType,
    AuthorStatusType,
    EndorseStatusType,
    Connection,
    ConnectionList,
)
from api.services.connections import (
    get_connections_list,
    get_connection_object,
    accept_connection_request,
    update_connection_info,
    update_connection_config,
)
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=ConnectionList)
async def get_connections(
    connection_state: Optional[ConnectionStateType] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> ConnectionList:
    try:
        (total_count, connections) = await get_connections_list(
            db,
            connection_state=connection_state.value if connection_state else None,
            page_size=page_size,
            page_num=page_num,
        )
        response: ConnectionList = ConnectionList(
            page_size=page_size,
            page_num=page_num,
            count=len(connections),
            total_count=total_count,
            connections=connections,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{connection_id}", response_model=Connection)
async def get_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    try:
        connection = await get_connection_object(db, connection_id)
        return connection
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{connection_id}", response_model=Connection)
async def update_connection(
    connection_id: str,
    alias: str,
    public_did: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    try:
        connection = await update_connection_info(db, connection_id, alias, public_did)
        return connection
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{connection_id}/configure", response_model=Connection)
async def configure_connection(
    connection_id: str,
    author_status: AuthorStatusType,
    endorse_status: EndorseStatusType,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    try:
        connection = await update_connection_config(
            db, connection_id, author_status, endorse_status
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{connection_id}/accept", response_model=Connection)
async def accept_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    """Manually accept a connection."""
    try:
        connection: Connection = await get_connection_object(db, connection_id)
        accepted_connection = await accept_connection_request(db, connection)
        return accepted_connection
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{connection_id}/reject", response_model=Connection)
async def reject_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    # TODO this should send a ProblemReport back to the requester
    raise NotImplementedError
