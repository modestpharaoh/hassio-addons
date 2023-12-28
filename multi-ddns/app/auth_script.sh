#!/bin/bash bashio

source /api_lib.sh

# bashio::log.level "debug"

# This script is called during the authentication phase to create the DNS TXT record.

# Replace these variables with your actual DNS provider credentials and details.

DUCKDNS_TOKEN=${Duck_Token}
DYNU_TOKEN=${Dynu_Token}
domain="$CERTBOT_DOMAIN"
TXT_NAME="_acme-challenge"
TXT_VALUE="$CERTBOT_VALIDATION"

bashio::log.debug "Trying to feed ${domain} with TXT record: ${TXT_VALUE}"

function challenge_verify() {
    TXT_RECORD="_acme-challenge.$domain"
    EXPECTED_TXT=$TXT_VALUE
    TIMEOUT_SECONDS=120
    CHECK_INTERVAL_SECONDS=10
    elapsed_time=0

    for ((i=0; i<TIMEOUT_SECONDS; i+=CHECK_INTERVAL_SECONDS)); do
        # Check the DNS TXT record using dig
        txt_value=$(dig +short TXT @8.8.8.8 ${TXT_RECORD})

        # Remove double quotes from the TXT value (if present)
        txt_value="${txt_value//\"/}"

        bashio::log.debug "Current TXT value for $TXT_RECORD: $txt_value"

        # Check if the TXT value matches the expected value
        if [ "$txt_value" == "$EXPECTED_TXT" ]; then
            bashio::log.debug "Found expected TXT value. Exiting in few seconds!"
            sleep 20
            exit 0
        fi

        # Sleep for the specified interval
        sleep $CHECK_INTERVAL_SECONDS

        # Update the elapsed time
        elapsed_time=$((elapsed_time + CHECK_INTERVAL_SECONDS))

        # Check if the total elapsed time exceeds the timeout
        if [ $elapsed_time -ge $TIMEOUT_SECONDS ]; then
            bashio::log.debug "Timeout reached. Exiting!"
            exit 1
        fi
    done
}


if [[ $domain == *"duckdns.org" ]]; then
    bashio::log.debug "DuckDNS deploy challenge..."
    rm_duck_txt_record "$domain" "$DUCKDNS_TOKEN"
    response=$(curl -s "https://www.duckdns.org/update?domains=${domain}&token=$DUCKDNS_TOKEN&txt=$TXT_VALUE&verbose=true")

    # Output the response (for debugging purposes)
    bashio::log.debug "DuckDNS Update Response: $response"
    challenge_verify
else
    bashio::log.debug "DynuDNS deploy challenge..."

    rm_dynu_txt_record "$domain" "$DYNU_TOKEN"

    # Get the ID of the Dynu domain
    DOMAINID=$(curl -s -X GET https://api.dynu.com/v2/dns -H "accept: application/json" -H \
            "API-Key: ${DYNU_TOKEN}"  | jq  --arg domain "$domain"  '.domains[]  | select(.name == $domain) | .id')
    bashio::log.debug "Dynu ${domain} ID:" "${DOMAINID}"


    # Feed the TXT challenge to Dynu domain
    resp=$(curl -s -X POST "https://api.dynu.com/v2/dns/${DOMAINID}/record" \
    -H "API-Key: $DYNU_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{
    "nodeName": "_acme-challenge",
    "recordType": "TXT",
    "textData": "'"$TXT_VALUE"'",
    "state": true,
    "ttl": 90
    }' )
    bashio::log.debug "Dynu challenge deploy response:" "${resp}"
    challenge_verify

fi