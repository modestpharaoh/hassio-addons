#!/bin/bash bashio

source /api_lib.sh

# bashio::log.level "debug"

DUCKDNS_TOKEN=${Duck_Token}
DYNU_TOKEN=${Dynu_Token}
domain="$CERTBOT_DOMAIN"
TXT_NAME="_acme-challenge"
TXT_VALUE="$CERTBOT_VALIDATION"


if [[ $domain == *"duckdns.org" ]]; then
    rm_duck_txt_record "$domain" "$DUCKDNS_TOKEN"
else
    rm_dynu_txt_record "$domain" "$DYNU_TOKEN"
fi