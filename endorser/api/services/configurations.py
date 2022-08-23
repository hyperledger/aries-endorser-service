import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from sqlalchemy.sql.functions import func

from api.endpoints.models.configurations import (
    ConfigurationType,
    CONFIG_DEFAULTS,
    ConfigurationSource,
    Configuration,
    config_to_db_object,
    db_to_config_object,
)
from api.db.models.configuration import ConfigurationDB
from api.db.errors import DoesNotExist


logger = logging.getLogger(__name__)

TRUE_VALUES = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']


async def db_add_db_config_record(db: AsyncSession, db_config: ConfigurationDB):
    logger.debug(f">>> adding config: {db_config} ...")
    db.add(db_config)
    await db.commit()


async def db_fetch_db_config_record(
    db: AsyncSession, config_name: str
) -> ConfigurationDB:
    logger.info(f">>> db_fetch_db_config_record() for {config_name}")
    q = select(ConfigurationDB).where(ConfigurationDB.config_name == config_name)
    result = await db.execute(q)
    result_rec = result.scalar_one_or_none()
    if not result_rec:
        raise DoesNotExist(
            f"{ConfigurationDB.__name__}<config_name:{config_name}> does not exist"
        )
    db_config: ConfigurationDB = ConfigurationDB.from_orm(result_rec)
    return db_config


async def db_update_db_config_record(
    db: AsyncSession, db_config: ConfigurationDB
) -> ConfigurationDB:
    if db_config.config_id is None:
        await db_add_db_config_record(db, db_config)
    else:
        logger.debug(f">>> updating config: {db_config} ...")
        payload_dict = db_config.dict()
        q = (
            update(ConfigurationDB)
            .where(ConfigurationDB.config_id == db_config.config_id)
            .where(ConfigurationDB.config_name == db_config.config_name)
            .values(payload_dict)
        )
        await db.execute(q)
        await db.commit()
    return await db_fetch_db_config_record(db, db_config.config_name)


async def db_get_config_records(db: AsyncSession) -> list[ConfigurationDB]:
    filters = []

    # build out a base query with all filters
    base_q = select(ConfigurationDB).filter(*filters)
    results_q_recs = await db.execute(base_q)
    db_configs = results_q_recs.scalars()

    return db_configs


async def get_config_record(db: AsyncSession, config_name: str) -> Configuration:
    try:
        db_config = await db_fetch_db_config_record(db, config_name)
        config = db_to_config_object(db_config)
        return config
    except DoesNotExist:
        config: Configuration = Configuration(
            config_id=None,
            config_name=ConfigurationType[config_name],
            config_value=os.getenv(config_name, CONFIG_DEFAULTS[config_name]),
            config_source=ConfigurationSource.Environment,
        )
        return config


async def get_config_records(db: AsyncSession) -> list[Configuration]:
    config_list = []
    for config_type in ConfigurationType:
        config = await get_config_record(db, config_type.name)
        config_list.append(config)
    return config_list


async def update_config_record(
    db: AsyncSession,
    config_name: str,
    config_value: str,
) -> Configuration:
    old_config = await get_config_record(db, config_name)
    old_config.config_value = config_value
    old_db_config = config_to_db_object(old_config)
    new_db_config = await db_update_db_config_record(db, old_db_config)
    new_config = db_to_config_object(new_db_config)
    return new_config


async def get_bool_config(db: AsyncSession, config_name: str) -> bool:
    config = await get_config_record(db, config_name)
    config_bool = config.config_value.lower() in TRUE_VALUES
    logger.debug(f"get_bool_config({config_name}) -> {config.config_value} = {config_bool}")
    return config_bool
