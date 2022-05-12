"""EndorseRequest Database Tables/Models.

Models of the Endorser tables for EndorseRequests (Author Endorse Requests)
and related data.

"""
import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field
from sqlalchemy import Column, func, text, String
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ARRAY

from api.db.models.base import BaseModel


class EndorseRequest(BaseModel, table=True):
    """EndorseRequest.

    This is the model for the EndorseRequest table
    (postgresql specific dialects in use).

    Attributes:
      endorse_request_id: Endorser's EndorseRequest ID
      contact_id: Endorser's Contact ID
      transaction_id: Underlying AcaPy transaction_id id
      connection_id: Underlying AcaPy connection id
      state: The underlying AcaPy transaction state
      created_at: Timestamp when record was created
      updated_at: Timestamp when record was last modified
    """

    endorse_request_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    # acapy data ---
    transaction_id: uuid.UUID = Field(nullable=False)
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    connection_id: uuid.UUID = Field(nullable=False)
    endorser_did: str = Field(nullable=False)
    author_did: str = Field(nullable=False)
    transaction_type: str = Field(nullable=False)
    state: str = Field(nullable=False)
    ledger_txn: str = Field(nullable=True, default=False)
    # --- acapy data

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )
