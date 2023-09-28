import logging
import traceback
from typing import cast, Any


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import api.acapy_utils as au

from api.core.config import settings
from api.db.models.allow import (
    AllowedSchema,
    AllowedCredentialDefinition,
)
from api.endpoints.models.allow import (
    AllowedPublicDid,
)
from api.endpoints.models.endorse import EndorseTransactionType
from sqlalchemy.engine.row import Row
from api.endpoints.models.endorse import (
    EndorseTransaction,
)

from attr import dataclass

from api.endpoints.models.endorse import (
    EndorseTransaction,
    webhook_to_txn_object,
)
from api.endpoints.models.connections import (
    webhook_to_connection_object,
    AuthorStatusType,
    EndorseStatusType,
    Connection,
)
from api.services.connections import (
    accept_connection_request,
    get_connection_object,
)
from api.services.configurations import (
    get_bool_config,
    get_config,
)
from api.services.endorse import (
    endorse_transaction,
    reject_transaction,
    get_endorser_did,
)


logger = logging.getLogger(__name__)


def is_auto_endorse_connection(connection: Connection) -> bool:
    # check if connection or author_did is setup for auto-endorse
    return (
        connection.author_status.name is AuthorStatusType.active.name
        and connection.endorse_status.name is EndorseStatusType.auto_endorse.name
    )


def is_auto_reject_connection(connection: Connection) -> bool:
    # check if connection or author_did is setup for auto-endorse
    return (
        connection.author_status.name is AuthorStatusType.active.name
        and connection.endorse_status.name is EndorseStatusType.auto_reject.name
    )


async def is_auto_endorse_txn(
    db: AsyncSession, transaction: EndorseTransaction, connection: Connection
):
    auto_req = await get_bool_config(db, "ENDORSER_AUTO_ENDORSE_REQUESTS")
    auto_req_type = await get_config(db, "ENDORSER_AUTO_ENDORSE_TXN_TYPES")
    if auto_req or is_auto_endorse_connection(connection):
        # auto-req is on, check if any txn types are configures
        if auto_req_type is None or len(auto_req_type) == 0:
            # nothing configured, auto-endorse-all
            return True
        txn_type = transaction.transaction_type
        auto_req_types = auto_req_type.split(",")
        return txn_type in auto_req_types

    return False


async def auto_step_ping_received(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    return {}


async def auto_step_connections_request(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # auto-accept connection?
    connection: Connection = webhook_to_connection_object(payload)
    if await get_bool_config(db, "ENDORSER_AUTO_ACCEPT_CONNECTIONS"):
        result = await accept_connection_request(db, connection)
    return {}


async def auto_step_connections_response(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # no-op
    return {}


async def auto_step_connections_active(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # no-op
    return {}


async def auto_step_connections_completed(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    # no-op
    return {}


@dataclass
class CreddefCriteria:
    DID: str
    Schema_Issuer_DID: str
    Schema_Name: str
    Schema_Version: str
    Tag: str
    RevRegDef: str
    RevRegEntry: str


@dataclass
class SchemaCriteria:
    DID: str
    Name: str
    Version: str


def eq_or_wild(indb, clause):
    return or_(indb == clause, indb == "*")


async def check_auto_endorse(
    db: AsyncSession,
    table: type,
    filters: list[tuple[Any, Any]],
) -> bool:
    wild_filters = [eq_or_wild(x, y) for x, y in filters]
    q = select(table).filter(*wild_filters)
    result = await db.execute(q)
    result_rec: Row | None = result.one_or_none()
    logger.debug(f"got the following record {result_rec} with query {q}")
    if result_rec:
        return True
    else:
        return False


async def allowed_publish_did(db: AsyncSession, did: str) -> bool:
    return await check_auto_endorse(
        db, AllowedPublicDid, [(AllowedPublicDid.registered_did, did)]
    )


async def allowed_schema(db: AsyncSession, schema_trans: SchemaCriteria) -> bool:
    return await check_auto_endorse(
        db,
        AllowedSchema,
        [
            (AllowedSchema.author_did, schema_trans.DID),
            (AllowedSchema.schema_name, schema_trans.Name),
            (AllowedSchema.version, schema_trans.Version),
        ],
    )


async def allowed_creddef(db: AsyncSession, creddef_trans: CreddefCriteria) -> bool:
    return await check_auto_endorse(
        db,
        AllowedCredentialDefinition,
        [
            (AllowedCredentialDefinition.author_did, creddef_trans.DID),
            (AllowedCredentialDefinition.issuer_did, creddef_trans.Schema_Issuer_DID),
            (AllowedCredentialDefinition.schema_name, creddef_trans.Schema_Name),
            (AllowedCredentialDefinition.version, creddef_trans.Schema_Version),
            (AllowedCredentialDefinition.tag, creddef_trans.Tag),
            (AllowedCredentialDefinition.rev_reg_def, creddef_trans.RevRegDef),
            (AllowedCredentialDefinition.rev_reg_entry, creddef_trans.RevRegEntry),
        ],
    )


async def allowed_p(db: AsyncSession, trans: EndorseTransaction) -> bool:
    logger.debug(f">>> from allowed_p: entered")
    # TODO check that this is how we want to handle this

    # Publishing/registering a public did on the ledger
    if (
        trans.author_goal_code == "aries.transaction.register_public_did"
        or trans.transaction_type == EndorseTransactionType.did
    ):
        return await allowed_publish_did(
            db,
            # The location of the DID depends on if the author already
            # has a public DID or not
            trans.transaction_request.get("did")
            if trans.author_goal_code == "aries.transaction.register_public_did"
            else trans.transaction.get("dest"),
        )
    else:
        # The author must already have a DID and a transaction in
        # order to do any of this
        if (not trans.author_did) or (not trans.transaction):
            return False

        match trans.transaction_type:
            case EndorseTransactionType.schema:
                logger.debug(f">>> from allowed_p: {trans} was a schema request")
                schema = trans.transaction["data"]
                s = SchemaCriteria(trans.author_did, schema["name"], schema["version"])
                logger.debug(f">>> from allowed_p: {trans} with schema {s}")
                return await allowed_schema(db, s)

            case EndorseTransactionType.cred_def:
                logger.debug(f">>> from allowed_p: {trans} was a cred_def request")

                sequence_num: int = cast(int, trans.transaction.get("ref"))

                response = cast(
                    dict, await au.acapy_GET("schemas/" + str(sequence_num))
                )

                logger.debug(
                    f">>> from allowed_p: {trans} was a cred_def request with response {response}"
                )
                schema_id: str = response["schema"]["id"]
                return await allowed_creddef(
                    db,
                    CreddefCriteria(
                        DID=trans.author_did,
                        Schema_Issuer_DID=schema_id.split(":")[0],
                        Schema_Name=schema_id.split(":")[2],
                        Schema_Version=schema_id.split(":")[3],
                        Tag=cast(str, trans.transaction.get("tag")),
                        # TODO determine what these are
                        RevRegEntry="true",
                        RevRegDef="true",
                    ),
                )

        return False


async def auto_step_endorse_transaction_request_received(
    db: AsyncSession, payload: dict, handler_result: dict
) -> EndorseTransaction | dict:
    logger.info(">>> in auto_step_endorse_transaction_request_received() ...")
    endorser_did = await get_endorser_did()
    transaction: EndorseTransaction = webhook_to_txn_object(payload, endorser_did)
    logger.debug(f">>> transaction = {transaction}")
    connection = await get_connection_object(db, transaction.connection_id)
    try:
        if is_auto_reject_connection(connection):
            logger.debug(
                f">>> from auto_step_endorse_transaction_request_received: this was not"
            )
            return await reject_transaction(db, transaction)
        elif await is_auto_endorse_txn(db, transaction, connection):
            logger.debug(
                f">>> from auto_step_endorse_transaction_request_received: this was allowed"
            )
            return await endorse_transaction(db, transaction)
        elif await allowed_p(db, transaction):
            logger.debug(
                f">>> from auto_step_endorse_transaction_request_received: {transaction} was allowed"
            )
            return await endorse_transaction(db, transaction)
        # If we could not auto endorse check if we should reject it or leave it pending
        elif await get_bool_config(db, "ENDORSER_REJECT_BY_DEFAULT"):
            return await reject_transaction(db, transaction)
        else:
            return {}
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(
            f">>> in handle_endorse_transaction_request_received: Failed to determine if the transaction should be endorsed with error: {e}"
        )
        return {}


async def auto_step_endorse_transaction_transaction_endorsed(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    logger.info(">>> in auto_step_endorse_transaction_transaction_endorsed() ...")
    return {}


async def auto_step_endorse_transaction_transaction_refused(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    logger.info(">>> in auto_step_endorse_transaction_transaction_refused() ...")
    return {}


async def auto_step_endorse_transaction_transaction_acked(
    db: AsyncSession, payload: dict, handler_result: dict
) -> dict:
    logger.info(">>> in auto_step_endorse_transaction_transaction_acked() ...")
    return {}
