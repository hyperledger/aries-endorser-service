import logging
from typing import List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.models.connections import (
    ConnectionProtocolType,
    ConnectionStateType,
    ConnectionRoleType,
    Connection,
)


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[Connection])
async def get_connections(
    connection_state: Optional[ConnectionStateType] = None,
):
    connections = []
    return connections


@router.get("/{connection_id}", response_model=Connection)
async def get_connection(
    connection_id: str,
):
    connection = None
    return connection


@router.put("/{connection_id}", response_model=Connection)
async def update_connection(
    connection_id: str,
    meta_data: dict,
):
    connection = None
    return connection


@router.post("/{connection_id}/configure", response_model=Connection)
async def configure_connection(
    connection_id: str,
    configuration: dict,
):
    connection = None
    return connection


@router.post("/{connection_id}/accept", response_model=Connection)
async def accept_connection(
    connection_id: str,
):
    connection = None
    return connection


@router.post("/{connection_id}/reject", response_model=Connection)
async def reject_connection(
    connection_id: str,
):
    connection = None
    return connection


@router.post("/{connection_id}/disable", response_model=Connection)
async def disable_connection(
    connection_id: str,
):
    connection = None
    return connection
