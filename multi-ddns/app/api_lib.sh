#!/usr/bin/env bashio

# bashio::log.level "debug"

# Fuction to get the Dynu Domain ID for the given domain and token
# Usage: get_dynu_domain_id "$domain" "$token"
function get_dynu_domain_id() {
    domain="$1"
    DYNU_TOKEN="${2}"

    repeat_count=3
    failed=0
    for ((i = 1; i <= repeat_count; i++)); do
        bashio::log.debug "Domain $domain: Attempt #$i: Calling Dynu API to get all domains..."
        # Getting the Dynu Domain ID for the given
        DynuDomainsResp=$(curl -s -f -m 20 -X GET https://api.dynu.com/v2/dns \
        -H "accept: application/json" \
        -H "API-Key: ${DYNU_TOKEN}")
        
        if [ $? -eq 0 ]; then
            failed=0
            break
        fi
        bashio::log.warning "Domain $domain: Attempt #$i: Failed Calling Dynu API to get all domains!"
        failed=1
    done
    if [ $failed -eq 0 ]; then
        bashio::log.debug "Domain $domain: Domains response:" "${DynuDomainsResp}"
        DynuDomainId=$(echo $DynuDomainsResp \
            | jq --arg domain "${domain}" '.domains[] | select(.name == $domain) | .id') 
        bashio::log.debug "Domain $domain: ID:" "${DynuDomainId}"
        echo "$DynuDomainId" # To return The domain
        return 0
    else
        bashio::log.warning "Domain $domain: Failed to get the domain ID multiple times!!!!"
        return 1
    fi
}

# Fuction to verify the propagation of the TXT record given the domain and the TXT value
# Usage: verify_challenge "$domain" "$expected_txt_value"
function verify_challenge() {
    domain="$1"
    EXPECTED_TXT=$2

    TXT_RECORD="_acme-challenge.$domain"
    TIMEOUT_SECONDS=120
    CHECK_INTERVAL_SECONDS=10
    elapsed_time=0

    bashio::log.debug "Domain $domain: Verify challenge before return..."
    for ((i=0; i<TIMEOUT_SECONDS; i+=CHECK_INTERVAL_SECONDS)); do
        # Check the DNS TXT record using dig
        txt_value=$(dig +short TXT @8.8.8.8 ${TXT_RECORD})

        # Remove double quotes from the TXT value (if present)
        txt_value="${txt_value//\"/}"

        bashio::log.debug "Domain $domain: Current TXT value for $TXT_RECORD: $txt_value"

        # Check if the TXT value matches the expected value
        if [ "$txt_value" == "$EXPECTED_TXT" ]; then
            bashio::log.debug "Domain $domain: Found expected TXT value. Exiting in few seconds!"
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
            return 1
        fi
    done
    return 0
}

# Fuction to deploy Duck DNS TXT record
# Usage: deploy_duck_txt_record "$domain" "$token" "$txt_value"
function deploy_duck_txt_record() {
    domain="$1"
    DUCKDNS_TOKEN="${2}"
    TXT_VALUE="${3}"

    bashio::log.debug "Domain $domain: DuckDNS deploy challenge..."
    response=$(curl -s "https://www.duckdns.org/update?domains=${domain}&token=$DUCKDNS_TOKEN&txt=$TXT_VALUE&verbose=true")

    # Output the response (for debugging purposes)
    bashio::log.debug "Domain $domain: DuckDNS Update Response: $response"
    verify_challenge "$domain" "$TXT_VALUE"
    return 0
}

# Fuction to deploy Dynu DNS TXT record
# Usage: deploy_dynu_txt_record "$domain" "$token" "$txt_value" "dynu_domain_id"
function deploy_dynu_txt_record() {
    domain="$1"
    DYNU_TOKEN="${2}"
    TXT_VALUE="${3}"
    DOMAINID=${4}
    bashio::log.debug "Domain $domain: DynuDNS deploy challenge..."

    repeat_count=3
    failed=0
    for ((i = 1; i <= repeat_count; i++)); do
        # Feed the TXT challenge to Dynu domain
        bashio::log.debug "Domain $domain : Attempt #$i: Updating TXT record..."
        resp=$(curl -s -m 10 -f -X POST "https://api.dynu.com/v2/dns/${DOMAINID}/record" \
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
        bashio::log.warning "Domain $domain :Attempt #$i: Failed updating TXT record!"
        failed=1
    done
    if [ $failed -eq 0 ]; then
        bashio::log.debug "Dynu challenge deploy response:" "${resp}"
    else
        bashio::log.warning "Domain $domain: Failed updating TXT record multiple times, Dynu seems to be unreachable!!!!"
    fi

    verify_challenge "$domain" "$TXT_VALUE"
    return 0
}

# Function to delete all TXT records for the Dynu DDNS domain
# Usage: rm_duck_txt_record "${domain}" "$token"
function rm_duck_txt_record() {
    domain="$1"
    DUCKDNS_TOKEN="${2}"

    bashio::log.debug "Domain $domain: Cleaning up DuckDNS TXT record..."
    clear_resp=$(curl -s -m 10 -f "https://www.duckdns.org/update?domains=$domain&token=$DUCKDNS_TOKEN&txt=removed&clear=true")
    bashio::log.debug "Domain $domain: Clear DuckDNS TXT record response:" "${clear_resp}"
    return 0
}


# Function to delete all TXT records for the Dynu DDNS domain
# Usage: rm_dynu_txt_records "${domain}" "$token" "$domain_id"
function rm_dynu_txt_records() {
    domain="$1"
    DYNU_TOKEN="${2}"
    DOMAINID=${3}

    bashio::log.debug "Domain $domain: Cleaning up Dynu TXT records..."

    repeat_count=3
    failed=0
    for ((i = 1; i <= repeat_count; i++)); do
        # Get DNS records for the Dynu domain
        bashio::log.debug "Domain $domain: Attempt #$i: Getting DNS records..."
        RECORDS=$(curl -s -m 10 -f -X GET https://api.dynu.com/v2/dns/$DOMAINID/record -H "accept: application/json" -H \
                "API-Key: ${DYNU_TOKEN}"  | jq -r '.dnsRecords[] | select(.recordType == "TXT")  | .id' )
        if [ $? -eq 0 ]; then
            failed=0
            break
        fi
        bashio::log.warning "Domain $domain: Attempt #$i: Failed To get Dynu DNS records!"
        failed=1
    done
    if [ $failed -eq 0 ]; then
        bashio::log.debug "DNS records response for domain $domain: ${RECORDS}"
        for record in $RECORDS; do
            bashio::log.debug "Domain $domain: Deleting record ID: $record"
            del_resp=$(curl -s -m 10 -f -X DELETE "https://api.dynu.com/v2/dns/${DOMAINID}/record/$record" \
            -H "API-Key: $DYNU_TOKEN" \
            -H "accept: application/json" )
            bashio::log.debug "Domain $domain: record ID $record: Delete response:" "${del_resp}"
        done
        return 0
    else
        bashio::log.warning "Domain $domain: Failed to get Dynu DNS records multiple times, Dynu seems to be unreachable!!!!"
        return 1
    fi
}