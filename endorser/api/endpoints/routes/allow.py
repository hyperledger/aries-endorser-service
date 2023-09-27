import logging
from typing import Optional, TypeVar
from sqlalchemy.sql.functions import func
from api.db.models.base import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, delete, and_
from api.db.errors import DoesNotExist
from starlette import status

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
from api.db.models.endorse_request import EndorseRequest

from api.services.endorse import (
    endorse_transaction,
)
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from api.services.auto_state_handlers import allowed_p

router = APIRouter()
logger = logging.getLogger(__name__)


# TODO add a try catch to avoid errors leaking
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


async def construct_getter(
    db: AsyncSession, filters: list, table: type[T], page_num, page_size
) -> tuple[int, list[T]]:
    skip = (page_num - 1) * page_size
    base_q = select(table).filter(*filters)
    count_q = select([func.count()]).select_from(base_q)
    q = base_q.limit(page_size).offset(skip)
    count_result = await db.execute(count_q)
    total_count: int = count_result.scalar()

    result = await db.execute(q)
    db_txn: list[T] = result.scalars().all()
    return (total_count, db_txn)


@router.get(
    "/publish-did",
    status_code=status.HTTP_200_OK,
    response_model=AllowedPublicDidList,
)
async def get_allowed_dids(
    did: Optional[str] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> AllowedPublicDidList:
    try:
        total_count: int
        db_txn: list[AllowedPublicDid]
        total_count, db_txn = await construct_getter(
            db, [], AllowedPublicDid, page_num, page_size
        )

        return AllowedPublicDidList(
            page_size=page_size,
            page_num=page_num,
            total_count=total_count,
            count=len(db_txn),
            connections=db_txn,
        )
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/publish-did/{did}",
    status_code=status.HTTP_200_OK,
    response_model=AllowedPublicDid,
)
async def get_allowed_did(
    did: str,
    db: AsyncSession = Depends(get_db),
) -> AllowedPublicDid:
    try:
        q = select(AllowedPublicDid).where(AllowedPublicDid.registered_did == did)
        result = await db.execute(q)
        result_rec = result.scalar_one_or_none()
        if not result_rec:
            raise DoesNotExist(
                f"{AllowedPublicDid.__name__}<transaction_id:{did}> does not exist"
            )

        db_txn: AllowedPublicDid = AllowedPublicDid.from_orm(result_rec)
        return db_txn
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/publish-did/{did}",
    status_code=status.HTTP_200_OK,
    response_model=AllowedPublicDid,
)
async def add_allowed_did(
    did: str,
    db: AsyncSession = Depends(get_db),
) -> AllowedPublicDid:
    try:
        tmp = AllowedPublicDid(registered_did=did)
        db.add(tmp)
        await db.commit()
        await updated_allowed(db)
        return tmp
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# TODO make the result just a 200 or an error
@router.delete(
    "/publish-did/{did}",
    status_code=status.HTTP_200_OK,
    response_model=dict,
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
)
async def get_allowed_schemas(
    author_did: Optional[str] = None,
    schema_name: Optional[str] = None,
    version: Optional[str] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> AllowedSchemaList:
    try:
        filter = [
            (AllowedSchema.author_did == author_did if author_did else True),
            (AllowedSchema.schema_name == schema_name if schema_name else True),
            (AllowedSchema.version == version if version else True),
        ]

        db_txn: list[AllowedSchema]
        total_count, db_txn = await construct_getter(
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
)
async def add_allowed_schema(
    author_did: Optional[str] = None,
    schema_name: Optional[str] = None,
    version: Optional[str] = None,
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
)
async def delete_allowed_schema(
    allowed_schema_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        q = delete(AllowedSchema).where(
            AllowedSchema.allowed_schema_id == AllowedSchema.allowed_schema_id
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
)
async def get_allowed_cred_def(
    issuer_did: Optional[str] = None,
    author_did: Optional[str] = None,
    schema_name: Optional[str] = None,
    version: Optional[str] = None,
    tag: Optional[str] = None,
    rev_reg_def: Optional[str] = None,
    rev_reg_entry: Optional[str] = None,
    page_size: int = 10,
    page_num: int = 1,
    db: AsyncSession = Depends(get_db),
) -> AllowedCredentialDefinitionList:
    try:
        filters = [
            AllowedCredentialDefinition.issuer_did == issuer_did
            if issuer_did
            else True,
            AllowedCredentialDefinition.author_did == author_did
            if author_did
            else True,
            AllowedCredentialDefinition.schema_name == schema_name
            if schema_name
            else True,
            AllowedCredentialDefinition.version == version if version else True,
            AllowedCredentialDefinition.tag == tag if tag else True,
            AllowedCredentialDefinition.rev_reg_def == rev_reg_def
            if rev_reg_def
            else True,
            AllowedCredentialDefinition.rev_reg_entry == rev_reg_entry
            if rev_reg_entry
            else True,
        ]

        db_txn: list[AllowedCredentialDefinition]
        total_count, db_txn = await construct_getter(
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
)
async def add_allowed_cred_def(
    issuer_did: Optional[str] = None,
    author_did: Optional[str] = None,
    schema_name: Optional[str] = None,
    version: Optional[str] = None,
    tag: Optional[str] = None,
    rev_reg_def: Optional[str] = None,
    rev_reg_entry: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> AllowedCredentialDefinition:
    try:
        tmp = AllowedCredentialDefinition(
            issuer_did=issuer_did,
            author_did=author_did,
            schema_name=schema_name,
            tag=tag,
            rev_reg_def=rev_reg_def,
            rev_reg_entry=rev_reg_entry,
            version=version,
        )
        db.add(tmp)
        await db.commit()
        await updated_allowed(db)
        return tmp
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/credential-definition",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def delete_allowed_cred_def(
    issuer_did: Optional[str] = None,
    author_did: Optional[str] = None,
    schema_name: Optional[str] = None,
    version: Optional[str] = None,
    tag: Optional[str] = None,
    rev_reg_def: Optional[str] = None,
    rev_reg_entry: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        q = delete(AllowedCredentialDefinition).where(
            and_(
                AllowedCredentialDefinition.issuer_did == issuer_did
                if issuer_did
                else True,
                AllowedCredentialDefinition.author_did == author_did
                if author_did
                else True,
                AllowedCredentialDefinition.schema_name == schema_name
                if schema_name
                else True,
                AllowedCredentialDefinition.version == version if version else True,
                AllowedCredentialDefinition.tag == tag if tag else True,
                AllowedCredentialDefinition.rev_reg_def == rev_reg_def
                if rev_reg_def
                else True,
                AllowedCredentialDefinition.rev_reg_entry == rev_reg_entry
                if rev_reg_entry
                else True,
            )
        )
        await db.execute(q)
        await updated_allowed(db)
        return {}
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
