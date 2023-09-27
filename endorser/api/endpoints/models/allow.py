from enum import Enum
import logging

from pydantic import BaseModel

from api.db.models.allow import (
    AllowedPublicDid,
    AllowedSchema,
    AllowedCredentialDefinition,
)


logger = logging.getLogger(__name__)


class AllowedPublicDidList(BaseModel):
    page_size: int
    page_num: int
    count: int
    total_count: int
    connections: list[AllowedPublicDid]


class AllowedSchemaList(BaseModel):
    page_size: int
    page_num: int
    count: int
    total_count: int
    connections: list[AllowedSchema]


class AllowedCredentialDefinitionList(BaseModel):
    page_size: int
    page_num: int
    count: int
    total_count: int
    connections: list[AllowedCredentialDefinition]
