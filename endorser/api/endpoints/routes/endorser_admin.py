import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.configurations import ConfigurationType
from api.services.admin import (
    get_endorser_configs,
    get_endorser_config,
    validate_endorser_config,
    update_endorser_config,
)
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config", status_code=status.HTTP_200_OK, response_model=dict)
async def get_config(
    db: AsyncSession = Depends(get_db),
) -> dict:
    # this should take some query params, sorting and paging params...
    try:
        endorser_configs = await get_endorser_configs(db)
        return endorser_configs
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/config/{config_name}", status_code=status.HTTP_200_OK, response_model=dict
)
async def get_config(
    config_name: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # this should take some query params, sorting and paging params...
    try:
        endorser_config = await get_endorser_config(db, config_name)
        return endorser_config
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/config/{config_name}", status_code=status.HTTP_200_OK, response_model=dict
)
async def update_config(
    config_name: str,
    config_value: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # throws an exception if we get an invalid config name
    try:
        config_type = ConfigurationType[config_name]
        validate_endorser_config(config_name, config_value)
        endorser_config = await update_endorser_config(db, config_name, config_value)
        return endorser_config
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
