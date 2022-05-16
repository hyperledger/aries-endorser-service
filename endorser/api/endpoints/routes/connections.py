import logging
from typing import List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.connections import (
    ConnectionProtocolType,
    ConnectionStateType,
    ConnectionRoleType,
    Connection,
    ConnectionList,
)
from api.services.connections import (
    get_connections_list,
    get_connection_object,
    accept_connection_request,
)


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=ConnectionList)
async def get_connections(
    connection_state: Optional[ConnectionStateType] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> ConnectionList:
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


@router.get("/{connection_id}", response_model=Connection)
async def get_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    connection = await get_connection_object(db, connection_id)
    return connection


@router.put("/{connection_id}", response_model=Connection)
async def update_connection(
    connection_id: str,
    meta_data: dict,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    connection = None
    return connection


@router.post("/{connection_id}/configure", response_model=Connection)
async def configure_connection(
    connection_id: str,
    configuration: dict,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    connection = None
    return connection


@router.post("/{connection_id}/accept", response_model=Connection)
async def accept_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    """Manually accept a connection."""
    connection: Connection = await get_connection_object(db, connection_id)
    accepted_connection = await accept_connection_request(db, connection)
    return accepted_connection


@router.post("/{connection_id}/reject", response_model=Connection)
async def reject_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    connection = None
    return connection


@router.post("/{connection_id}/disable", response_model=Connection)
async def disable_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Connection:
    connection = None
    return connection
