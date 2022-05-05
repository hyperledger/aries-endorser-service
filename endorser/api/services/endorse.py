import logging

from api.core.config import settings
from api.endpoints.models.endorse import EndorseTransactionState
import api.acapy_utils as au


logger = logging.getLogger(__name__)


async def handle_endorse_transaction(payload: dict):
    """Hande transaction endorse requests."""
    # TODO state-specific handling
    state = payload.get("state")
    if (state == EndorseTransactionState.request_received):
        # TODO ...check if auto-endorse
        pass
    else:
        logger.warn(f">>> unhandled transaction state {state}")
