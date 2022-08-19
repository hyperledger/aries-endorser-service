import logging

import api.acapy_utils as au


logger = logging.getLogger(__name__)



async def get_endorser_configs() -> dict:
    acapy_config = await au.acapy_GET(
        "status/config",
    )

    endorser_public_did = await au.acapy_GET(
        "wallet/did/public",
    )

    return {
        "acapy_config": acapy_config["config"],
        "endorser_config": {
            "public_did": endorser_public_did["result"]
        }
    }
