"""AllowedPublicDid Database Tables/Models.

Models of the Endorser tables for allow list and related data.

"""
import uuid
from datetime import datetime

from sqlmodel import Field
from sqlalchemy import Column, func
from sqlalchemy.engine.default import DefaultExecutionContext
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
      details:        Additional details related to this schema
    """

    # acapy data ---
    registered_did: str = Field(nullable=False, default=None, primary_key=True)
    details: str = Field(nullable=True, default=None)
    # --- acapy data

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )


def allowed_schema_uuid(context: DefaultExecutionContext):
    pr = context.get_current_parameters()
    return uuid.uuid5(
        uuid.NAMESPACE_OID,
        pr["author_did"] + pr["schema_name"] + pr["version"],
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
      details: Additional details related to this schema
    """

    # acapy data ---
    author_did: str = Field(nullable=False, default=None)
    schema_name: str = Field(nullable=False, default=None)
    version: str = Field(nullable=False, default=None)
    details: str = Field(nullable=True, default=None)
    # --- acapy data

    allowed_schema_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            default=allowed_schema_uuid,
            primary_key=True,
        )
    )

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )


def allowed_cred_def_uuid(context: DefaultExecutionContext):
    pr = context.get_current_parameters()
    return uuid.uuid5(
        uuid.NAMESPACE_OID,
        pr["issuer_did"]
        + pr["author_did"]
        + pr["schema_name"]
        + pr["version"]
        + pr["tag"]
        # We don't include rev_reg_def or rev_reg_entry since they
        # describe what a credential definition supports not the
        # credential-definition its self
        ,
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
      details: Additional details related to this credential definition
    """

    # acapy data ---
    issuer_did: str = Field(nullable=False, default=None)
    author_did: str = Field(nullable=False, default=None)
    schema_name: str = Field(nullable=False, default=None)
    version: str = Field(nullable=False, default=None)
    tag: str = Field(nullable=False, default=None)
    rev_reg_def: bool = Field(nullable=False, default=None)
    rev_reg_entry: bool = Field(nullable=False, default=None)
    details: str = Field(nullable=True, default=None)
    # --- acapy data

    allowed_cred_def_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            default=allowed_cred_def_uuid,
            primary_key=True,
        )
    )

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )
