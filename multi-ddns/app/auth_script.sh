#!/usr/bin/env bashio

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
            bashio::log.warning "Timeout reached. Exiting!"
            exit 0
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

      # Getting the Dynu Domain ID for the given domain
      DOMAINID=$(get_dynu_domain_id $domain $DYNU_TOKEN)
      if [ $? -eq 0 ]; then
        repeat_count=3
        failed=0
        for ((i = 1; i <= repeat_count; i++)); do
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
            if [ $? -eq 0 ]; then
                failed=0
                break
            fi
            failed=1
        done
        bashio::log.debug "Dynu challenge deploy response:" "${resp}"
        challenge_verify
      else
        bashio::log.warning "Failed to update public IP for domain ${domain}. SKIPPING this time..."
      fi

fi