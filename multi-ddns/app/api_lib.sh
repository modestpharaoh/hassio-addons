#!/usr/bin/env bashio

# bashio::log.level "debug"

TXT_NAME="_acme-challenge"

function verify_challenge() {
    domain="$1"
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


function deploy_duck_txt_record() {
    domain="$1"
    DUCKDNS_TOKEN="${2}"
    TXT_VALUE="${3}"

    bashio::log.debug "DuckDNS deploy challenge..."
    response=$(curl -s "https://www.duckdns.org/update?domains=${domain}&token=$DUCKDNS_TOKEN&txt=$TXT_VALUE&verbose=true")

    # Output the response (for debugging purposes)
    bashio::log.debug "DuckDNS Update Response: $response"
    verify_challenge "$domain"
    return 0
}

function deploy_dynu_txt_record() {
    domain="$1"
    DYNU_TOKEN="${2}"
    TXT_VALUE="${3}"
    bashio::log.debug "DynuDNS deploy challenge..."

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
    verify_challenge "$domain"
    return 0
}

function rm_duck_txt_record() {
    domain="$1"
    DUCKDNS_TOKEN="${2}"
    clear_resp=$(curl -s "https://www.duckdns.org/update?domains=$domain&token=$DUCKDNS_TOKEN&txt=removed&clear=true")
    bashio::log.debug "Clear DuckDNS TXT record response:" "${clear_resp}"
    return 0
}

function rm_dynu_txt_record() {
    domain="$1"
    DYNU_TOKEN="${2}"
    bashio::log.debug "Clean up Dynu TXT records..."
    # Get the ID of the Dynu domain
    DOMAINID=$(curl -s -X GET https://api.dynu.com/v2/dns -H "accept: application/json" -H \
            "API-Key: ${DYNU_TOKEN}"  | jq  --arg domain "$domain"  '.domains[]  | select(.name == $domain) | .id')
    bashio::log.debug "Dynu ${domain} ID:" "${DOMAINID}"

    # Get DNS records for the Dynu domain
    RECORDS=$(curl -s -X GET https://api.dynu.com/v2/dns/$DOMAINID/record -H "accept: application/json" -H \
            "API-Key: ${DYNU_TOKEN}"  | jq -r '.dnsRecords[] | select(.recordType == "TXT")  | .id' )
    bashio::log.debug "DNS Records related:" "${RECORDS}"
    for record in $RECORDS; do
        bashio::log.debug "Deleting record: $record"
        del_resp=$(curl -s -X DELETE "https://api.dynu.com/v2/dns/${DOMAINID}/record/$record" \
        -H "API-Key: $DYNU_TOKEN" \
        -H "accept: application/json" )
        bashio::log.debug "Delete record response:" "${del_resp}"
    done
    return 0
}