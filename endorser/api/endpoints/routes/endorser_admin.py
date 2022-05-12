import logging
from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic import BaseModel

from api.endpoints.dependencies.db import get_db


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config", status_code=status.HTTP_200_OK, response_model=dict)
async def get_config() -> dict:
    # this should take some query params, sorting and paging params...
    return {}
