#!/usr/bin/env bashio

source /api_lib.sh

# bashio::log.level "debug"

# This script is called during the authentication phase to clear the DNS TXT record.

DUCKDNS_TOKEN=${Duck_Token}
DYNU_TOKEN=${Dynu_Token}
domain="$CERTBOT_DOMAIN"
TXT_NAME="_acme-challenge"
TXT_VALUE="$CERTBOT_VALIDATION"


if [[ $domain == *"duckdns.org" ]]; then
    rm_duck_txt_record "$domain" "$DUCKDNS_TOKEN"
else
    # Getting the Dynu DNS domain IDs
    DOMAINID=$(get_dynu_domain_id $domain $DYNU_TOKEN)
    if [ $? -eq 0 ]; then
        rm_dynu_txt_records "$domain" "$DYNU_TOKEN" "$DOMAINID"
    else
        bashio::log.warning "Domain $domain: Can't delete TXT DNS records without the domain ID!!!"
    fi
fi