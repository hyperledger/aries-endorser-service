"""AllowedPublicDid Database Tables/Models.

Models of the Endorser tables for allow list and related data.

"""
import uuid
from datetime import datetime

from sqlmodel import Field
from sqlalchemy import Column, func, text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from api.db.models.base import BaseModel


class AllowedPublicDid(BaseModel, table=True):
    """AllowedPublicDid

    This is the model for the AllowPublicDid table
    (postgresql specific dialects in use).

    Attributes:
      registered_did: DIDs allowed to be registered
      created_at:     Timestamp when record was created
      updated_at:     Timestamp when record was last modified
    """

    # acapy data ---
    registered_did: str = Field(nullable=False, default=None, primary_key=True)
    # --- acapy data

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )


class AllowedSchema(BaseModel, table=True):
    """AllowedSchema

    This is the model for the AllowSchema table
    (postgresql specific dialects in use).

    Attributes:
      author_did: DID of the allowed author
      schema_name: Name of the schema
      version: Version of this schema
      created_at: Timestamp when record was created
      updated_at: Timestamp when record was last modified
    """

    # acapy data ---
    allowed_schema_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    author_did: str = Field(nullable=False, default=None)
    schema_name: str = Field(nullable=False, default=None)
    version: str = Field(nullable=False, default=None)
    # --- acapy data

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )


class AllowedCredentialDefinition(BaseModel, table=True):
    """AllowedCredentialDefinition

    This is the model for the AllowCredentialDefinition table
    (postgresql specific dialects in use).

    Attributes:
      issuer_did: DID of the issuer of the schema associated with this
                  credential definition
      author_did: DID of the author publishing the creddef
      schema_name: Name of the schema
      version: Version of this schema
      tag: tag of the creddef
      created_at: Timestamp when record was created
      updated_at: Timestamp when record was last modified
      rev_reg_def: If a revocation registration definition for this
                   credential should be endorsed
      rev_reg_entry: If the revocation registration entry for this
                     credential should be endorsed

    """

    # acapy data ---
    allowed_cred_def_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    issuer_did: str = Field(nullable=False, default=None)
    author_did: str = Field(nullable=False, default=None)
    schema_name: str = Field(nullable=False, default=None)
    version: str = Field(nullable=False, default=None)
    tag: str = Field(nullable=False, default=None)
    # TODO change to boolean
    rev_reg_def: str = Field(nullable=False, default=None)
    rev_reg_entry: str = Field(nullable=False, default=None)
    # --- acapy data

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )
