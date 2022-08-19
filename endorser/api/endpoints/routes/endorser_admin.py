import logging
from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic import BaseModel

from api.endpoints.dependencies.db import get_db
from api.services.admin import get_endorser_configs


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config", status_code=status.HTTP_200_OK, response_model=dict)
async def get_config() -> dict:
    # this should take some query params, sorting and paging params...
    endorser_configs = await get_endorser_configs()
    return endorser_configs
