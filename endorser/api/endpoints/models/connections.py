from enum import Enum
import logging

from pydantic import BaseModel

from api.db.models.contact import Contact


logger = logging.getLogger(__name__)


class ConnectionProtocolType(str, Enum):
    Connections = "connections/1.0"
    DIDExchange = "didexchange/1.0"


class ConnectionStateType(str, Enum):
    start = "start"
    init = "init"
    invitation = "invitation"
    request = "request"
    response = "response"
    active = "active"
    completed = "completed"
    abandoned = "abandoned"
    error = "error"


class ConnectionRoleType(str, Enum):
    inviter = "inviter"
    invitee = "invitee"
    requester = "requester"
    responder = "responder"


class Connection(BaseModel):
    connection_id: str
    alias: str | None = None
    author_status: str
    endorse_status: str
    tags: list[str]
    created_at: str | None = None
    updated_at: str | None = None
    state: str
    connection_protocol: str
    error_msg: str | None = None
    invitation: str | None = None
    my_did: str | None = None
    their_did: str | None = None
    their_label: str | None = None
    their_public_did: str | None = None
    their_role: str | None = None


class ConnectionList(BaseModel):
    page_size: int
    page_num: int
    count: int
    total_count: int
    connections: list[Connection]


def webhook_to_connection_object(payload: dict) -> Connection:
    """Convert from a webhook payload to a connection."""
    logger.debug(f">>> from payload: {payload}")
    connection: Connection = Connection(
        connection_id=payload.get("connection_id"),
        alias=payload.get("alias"),
        author_status="TBD",
        endorse_status="TBD",
        tags=[],
        state=payload.get("state"),
        connection_protocol=payload.get("connection_protocol"),
        error_msg=payload.get("error_msg"),
        invitation=payload.get("invitation"),
        my_did=payload.get("my_did"),
        their_did=payload.get("their_did"),
        their_label=payload.get("their_label"),
        their_public_did=payload.get("their_public_did"),
        their_role=payload.get("their_role"),
    )
    logger.debug(f">>> to connection: {connection}")
    return connection


def connection_to_db_object(connection: Connection) -> Contact:
    """Convert from model object to database model object."""
    logger.debug(f">>> from connection: {connection}")
    contact: Contact = Contact(
        author_status=connection.author_status,
        endorse_status=connection.endorse_status,
        tags=connection.tags,
        connection_id=connection.connection_id,
        connection_protocol=connection.connection_protocol,
        public_did=connection.their_public_did if connection.their_public_did else "",
        state=connection.state,
        connection_alias=connection.alias if connection.alias else "",
        their_label=connection.their_label,
    )
    logger.debug(f">>> to contact: {contact}")
    return contact


def db_to_connection_object(
    contact: Contact, acapy_connection: dict = None
) -> Connection:
    """Convert from database and acapy objects to model object."""
    connection: Connection = Connection(
        author_status=contact.author_status,
        endorse_status=contact.endorse_status,
        tags=contact.tags,
        connection_id=str(contact.connection_id),
        connection_protocol=contact.connection_protocol,
        their_public_did=contact.public_did,
        state=contact.state,
        alias=contact.connection_alias,
        their_label=contact.their_label,
        created_at=str(contact.created_at),
        updated_at=str(contact.updated_at),
    )
    if acapy_connection:
        connection.error_msg = acapy_connection.get("error_msg")
        connection.invitation = acapy_connection.get("invitation")
        connection.my_did = acapy_connection.get("my_did")
        connection.their_label = acapy_connection.get("their_label")
        connection.their_role = acapy_connection.get("their_role")
    return connection
