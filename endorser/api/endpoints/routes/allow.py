import logging
from typing import Optional, TypeVar, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.sql.functions import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from api.endpoints.models.endorse import (
    EndorseTransactionState,
    db_to_txn_object,
)

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.allow import (
    AllowedPublicDidList,
    AllowedPublicDid,
    AllowedSchemaList,
    AllowedCredentialDefinitionList,
)
from api.db.models.allow import (
    AllowedSchema,
    AllowedCredentialDefinition,
)
from api.db.errors import DoesNotExist
from api.db.models.endorse_request import EndorseRequest

from api.services.endorse import (
    endorse_transaction,
)
from api.services.auto_state_handlers import allowed_p

router = APIRouter()
logger = logging.getLogger(__name__)


async def updated_allowed(db: AsyncSession) -> None:
    try:
        q = select(EndorseRequest).where(
            EndorseRequest.state == EndorseTransactionState.request_received
        )
        result = await db.execute(q)
        db_txns: list[EndorseRequest] = result.scalars().all()
        for txn in db_txns:
            transaction = db_to_txn_object(txn, acapy_txn=None)
            logger.debug(
                f">>> from updated_allowed: the current transaction is {transaction}"
            )
            was_allowed = await allowed_p(db, transaction)
            logger.debug(f">>> from updated_allowed: this was allowed? {was_allowed}")
            if was_allowed:
                logger.debug(
                    f">>> from updated_allowed: endorsing transaction: {transaction}"
                )
                await endorse_transaction(db, transaction)
    except Exception as e:
        # try to retrieve and print text on error
        logger.error("Failed to update pending transactions ", e)


T = TypeVar("T")
J = TypeVar("J")


async def select_from_table(
    db: AsyncSession,
    filters: dict[J | None, J],
    table: type[T],
    page_num,
    page_size,
) -> tuple[int, list[T]]:
    skip = (page_num - 1) * page_size
    filter_conditions = [
        cond == value if value else True for value, cond in filters.items()
    ]
    base_q = select(table).filter(*filter_conditions)
    count_q = select([func.count()]).select_from(base_q)
    q = base_q.limit(page_size).offset(skip)
    count_result = await db.execute(count_q)
    total_count: int = count_result.scalar()

    result = await db.execute(q)
    db_txn: list[T] = result.scalars().all()
    return (total_count, db_txn)


@router.post(
    "/publish-did/{did}",
    status_code=status.HTTP_200_OK,
    response_model=AllowedPublicDid,
    description="Add a new DID that will be auto endorsed when published by an author",
)
async def add_allowed_did(
    did: str = "*",
    db: AsyncSession = Depends(get_db),
) -> AllowedPublicDid:
    try:
        adid = AllowedPublicDid(registered_did=did)
        db.add(adid)
        await db.commit()
        await updated_allowed(db)
        return adid
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/publish-did/{did}",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    description="Remove a DID from the list of DIDs that will be auto endorsed when published to the ledger",
)
async def delete_allowed_did(
    did: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        q = delete(AllowedPublicDid).where(AllowedPublicDid.registered_did == did)
        await db.execute(q)
        await updated_allowed(db)
        return {}
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/schema",
    status_code=status.HTTP_200_OK,
    response_model=AllowedSchemaList,
    description="Get a list of schemas that will be auto endorsed when sent to the ledger by an author",
)
async def get_allowed_schemas(
    allowed_schema_id: Optional[UUID] = None,
    author_did: Optional[str] = None,
    schema_name: Optional[str] = None,
    version: Optional[str] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> AllowedSchemaList:
    try:
        filter = {
            allowed_schema_id: AllowedSchema.allowed_schema_id,
            author_did: AllowedSchema.author_did,
            schema_name: AllowedSchema.schema_name,
            version: AllowedSchema.version,
        }

        db_txn: list[AllowedSchema]
        total_count, db_txn = await select_from_table(
            db, filter, AllowedSchema, page_num, page_size
        )
        return AllowedSchemaList(
            page_size=page_size,
            page_num=page_num,
            total_count=total_count,
            count=len(db_txn),
            connections=db_txn,
        )
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/schema",
    status_code=status.HTTP_200_OK,
    response_model=AllowedSchema,
    description="Add a new schema that will be auto endorsed when sent to the ledger by an author",
)
async def add_allowed_schema(
    author_did: str = "*",
    schema_name: str = "*",
    version: str = "*",
    db: AsyncSession = Depends(get_db),
) -> AllowedSchema:
    try:
        tmp = AllowedSchema(
            author_did=author_did, schema_name=schema_name, version=version
        )
        db.add(tmp)
        await db.commit()
        await updated_allowed(db)
        return tmp
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/schema",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    description="Remove a schema from the list of schemas that will be auto endorsed when sent to the ledger",
)
async def delete_allowed_schema(
    allowed_schema_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        q = delete(AllowedSchema).where(
            AllowedSchema.allowed_schema_id == allowed_schema_id
        )
        await db.execute(q)
        await updated_allowed(db)
        return {}
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/credential-definition",
    status_code=status.HTTP_200_OK,
    response_model=AllowedCredentialDefinitionList,
    description="Get a list of credential definitions that will be auto endorsed when sent to the ledger by an author",
)
async def get_allowed_cred_def(
    allowed_cred_def_id: Optional[UUID] = None,
    issuer_did: Optional[str] = None,
    author_did: Optional[str] = None,
    schema_name: Optional[str] = None,
    version: Optional[str] = None,
    tag: Optional[str] = None,
    rev_reg_def: Optional[bool] = None,
    rev_reg_entry: Optional[bool] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> AllowedCredentialDefinitionList:
    try:
        filters = {
            allowed_cred_def_id: AllowedCredentialDefinition.allowed_cred_def_id,
            issuer_did: AllowedCredentialDefinition.issuer_did,
            author_did: AllowedCredentialDefinition.author_did,
            schema_name: AllowedCredentialDefinition.schema_name,
            version: AllowedCredentialDefinition.version,
            tag: AllowedCredentialDefinition.tag,
            str(rev_reg_def)
            if rev_reg_def
            else None: AllowedCredentialDefinition.rev_reg_def,
            str(rev_reg_entry)
            if rev_reg_entry
            else None: AllowedCredentialDefinition.rev_reg_entry,
        }

        db_txn: list[AllowedCredentialDefinition]
        total_count, db_txn = await select_from_table(
            db, filters, AllowedCredentialDefinition, page_num, page_size
        )
        await updated_allowed(db)
        return AllowedCredentialDefinitionList(
            page_size=page_size,
            page_num=page_num,
            total_count=total_count,
            count=len(db_txn),
            connections=db_txn,
        )
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/credential-definition",
    status_code=status.HTTP_200_OK,
    response_model=AllowedCredentialDefinition,
    description="Add a new credential definition that will be auto endorsed when sent to the ledger by an author",
)
async def add_allowed_cred_def(
    issuer_did: str = "*",
    author_did: str = "*",
    schema_name: str = "*",
    version: str = "*",
    tag: str = "*",
    rev_reg_def: bool = True,
    rev_reg_entry: bool = True,
    db: AsyncSession = Depends(get_db),
) -> AllowedCredentialDefinition:
    try:
        acreddef = AllowedCredentialDefinition(
            issuer_did=issuer_did,
            author_did=author_did,
            schema_name=schema_name,
            tag=tag,
            rev_reg_def=str(rev_reg_def),
            rev_reg_entry=str(rev_reg_entry),
            version=version,
        )
        db.add(acreddef)
        await db.commit()
        await updated_allowed(db)
        return acreddef
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/credential-definition",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    description="Remove a credential definition from the list of credential definitions that will be auto endorsed when sent to the ledger",
)
async def delete_allowed_cred_def(
    allowed_cred_def_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        q = delete(AllowedCredentialDefinition).where(
            AllowedCredentialDefinition.allowed_cred_def_id == allowed_cred_def_id
        )
        await db.execute(q)
        await updated_allowed(db)
        return {}
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
