#!/bin/bash

# based on code developed by Sovrin:  https://github.com/hyperledger/aries-acapy-plugin-toolbox

if [[ "${ENDORSER_ENV}" == "local" ]]; then
	echo "using ngrok end point [$NGROK_NAME]"

	NGROK_ENDPOINT=null
	while [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]
	do
	    echo "Fetching end point from ngrok service"
	    NGROK_ENDPOINT=$(curl --silent $NGROK_NAME:4040/api/tunnels | ./jq -r '.tunnels[] | select(.proto=="https") | .public_url')

	    if [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]; then
	        echo "ngrok not ready, sleeping 5 seconds...."
	        sleep 5
	    fi
	done

	export ACAPY_ENDPOINT=$NGROK_ENDPOINT
fi

echo "Starting aca-py agent with endpoint [$ACAPY_ENDPOINT]"

# ... if you want to echo the aca-py startup command ...
set -x

exec aca-py start \
    --auto-provision \
    --inbound-transport http '0.0.0.0' ${ACAPY_HTTP_PORT} \
    --outbound-transport http \
    --webhook-url "${ENDORSER_WEBHOOK_URL}" \
    --genesis-url "${GENESIS_URL}" \
    --endpoint "${ACAPY_ENDPOINT}" \
    --auto-accept-invites \
    --auto-accept-requests \
    --auto-respond-messages \
    --auto-ping-connection \
    --monitor-ping \
    --public-invites \
    --wallet-type "indy" \
    --wallet-name "${ACAPY_WALLET_DATABASE}" \
    --wallet-key "${ACAPY_WALLET_ENCRYPTION_KEY}" \
    --wallet-storage-type "${ACAPY_WALLET_STORAGE_TYPE}" \
    --wallet-storage-config "{\"url\":\"${POSTGRESQL_HOST}:5432\",\"max_connections\":5}" \
    --wallet-storage-creds "{\"account\":\"${POSTGRESQL_USER}\",\"password\":\"${POSTGRESQL_PASSWORD}\",\"admin_account\":\"${POSTGRESQL_USER}\",\"admin_password\":\"${POSTGRESQL_PASSWORD}\"}" \
    --wallet-name "${ACAPY_WALLET_DATABASE}"  \
    --seed "${ENDORSER_SEED}" \
    --admin '0.0.0.0' ${ACAPY_ADMIN_PORT} \
    --label "${AGENT_NAME}" \
    ${ACAPY_ADMIN_CONFIG} \
    --endorser-protocol-role endorser \
    --auto-endorse-transactions \
    --log-level "${LOG_LEVEL}" \
