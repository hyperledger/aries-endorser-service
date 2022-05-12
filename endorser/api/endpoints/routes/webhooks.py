from enum import Enum
import logging
import traceback

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from api.core.config import settings
from api.endpoints.dependencies.db import get_db
import api.services as api_services

import api.acapy_utils as au


logger = logging.getLogger(__name__)

router = APIRouter()

api_key_header = APIKeyHeader(
    name=settings.ACAPY_WEBHOOK_URL_API_KEY_NAME, auto_error=False
)


class WebhookTopicType(str, Enum):
    ping = "ping"
    connections = "connections"
    oob_invitation = "oob-invitation"
    connection_reuse = "connection-reuse"
    connection_reuse_accepted = "connection-reuse-accepted"
    basicmessages = "basicmessages"
    issue_credential = "issue-credential"
    issue_credential_v2_0 = "issue-credential-v2-0"
    issue_credential_v2_0_indy = "issue-credential-v2-0-indy"
    issue_credential_v2_0_ld_proof = "issue-credential-v2-0-ld-proof"
    issuer_cred_rev = "issuer-cred-rev"
    present_proof = "present-proof"
    present_proof_v2_0 = "present-proof-v2-0"
    endorse_transaction = "endorse_transaction"
    revocation_registry = "revocation-registry"
    revocation_notification = "revocation-notification"
    problem_report = "problem-report"


async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header == settings.ACAPY_WEBHOOK_URL_API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


def get_webhookapp() -> FastAPI:
    application = FastAPI(
        title="WebHooks",
        description="Endpoints for Aca-Py WebHooks",
        debug=settings.DEBUG,
        middleware=None,
    )
    application.include_router(router, prefix="")
    return application


@router.post("/topic/{topic}/", response_model=dict)
async def process_webhook(
    topic: WebhookTopicType,
    payload: dict,
    api_key: APIKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Called by aca-py agent."""
    state = payload.get("state")
    if state:
        logger.info(f">>> Called webhook for endorser: {topic} / {state}")
    else:
        logger.info(f">>> Called webhook for endorser: {topic}")
    logger.debug(f">>> payload: {payload}")

    # call the handler to process the hook, if present
    result = {}
    try:
        handler = f"handle_{topic}_{state}" if state else f"handle_{topic}"
        handler = handler.replace("-", "_")
        if hasattr(api_services, handler):
            result = await getattr(api_services, handler)(db, payload)
            logger.debug(f">>> {handler} returns = {result}")
        else:
            logger.warn(f">>> no webhook handler available for: {handler}")
    except Exception as e:
        logger.error(">>> handler returned error:" + str(e))
        traceback.print_exc()
        return result

    try:
        # call the "auto-stepper" if we have one, to move to the next state
        stepper = f"auto_step_{topic}_{state}" if state else f"auto_step_{topic}"
        stepper = stepper.replace("-", "_")
        if hasattr(api_services, stepper):
            _stepper_result = await getattr(api_services, stepper)(db, payload, result)
            logger.debug(f">>> {stepper} returns = {_stepper_result}")
        else:
            logger.warn(f">>> no webhook stepper available for: {stepper}")
    except Exception as e:
        logger.error(">>> auto-stepper returned error:" + str(e))
        traceback.print_exc()

    return result
