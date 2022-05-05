import logging

from api.core.config import settings
from api.endpoints.models.connections import ConnectionProtocolType, ConnectionStateType
from api.endpoints.models.endorse import EndorserRoleType

import api.acapy_utils as au


logger = logging.getLogger(__name__)


async def handle_endorser_connection(payload: dict):
    """Set endorser role on any connections we receive."""
    # TODO check final state for other connections protocols
    if (payload["state"] == ConnectionProtocolType.completed and payload["connection_protocol"] == ConnectionProtocolType.DIDExchange):
        # confirm if we have already set the role on this connection
        connection_id = payload["connection_id"]
        logger.debug(f">>> check for metadata on connection: {connection_id}")
        conn_meta_data = await au.acapy_GET(f"connections/{connection_id}/metadata")
        if "transaction-jobs" in conn_meta_data["results"]:
            if "transaction_my_job" in conn_meta_data["results"]["transaction-jobs"]:
                return

        # set our endorser role
        logger.debug(f">>> Setting meta-data for connection: {payload}")
        params = {"transaction_my_job": EndorserRoleType.Endorser}
        await au.acapy_POST(
            f"transactions/{connection_id}/set-endorser-role", params=params
        )
