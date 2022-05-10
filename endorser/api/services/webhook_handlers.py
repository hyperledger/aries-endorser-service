import logging

from api.core.config import settings
from api.endpoints.models.connections import ConnectionProtocolType, ConnectionStateType
from api.endpoints.models.endorse import EndorserRoleType, EndorseTransactionState
import api.acapy_utils as au


logger = logging.getLogger(__name__)


async def handle_ping(payload: dict) -> dict:
    logger.info(">>> in handle_ping() ...")
    return {}


async def handle_connections_completed(payload: dict):
    """Set endorser role on any connections we receive."""
    # TODO check final state for other connections protocols
    if payload["connection_protocol"] == ConnectionProtocolType.DIDExchange.value:
        # confirm if we have already set the role on this connection
        connection_id = payload["connection_id"]
        logger.info(f">>> check for metadata on connection: {connection_id}")
        conn_meta_data = await au.acapy_GET(f"connections/{connection_id}/metadata")
        if "transaction-jobs" in conn_meta_data["results"]:
            if "transaction_my_job" in conn_meta_data["results"]["transaction-jobs"]:
                return

        # set our endorser role
        params = {"transaction_my_job": EndorserRoleType.Endorser.value}
        logger.info(f">>> Setting meta-data for connection: {payload}, with params: {params}")
        await au.acapy_POST(
            f"transactions/{connection_id}/set-endorser-role", params=params
        )
    return {}


async def handle_endorse_transaction_request_received(payload: dict):
    """Hande transaction endorse requests."""
    # TODO ...check if auto-endorse
    return {}
