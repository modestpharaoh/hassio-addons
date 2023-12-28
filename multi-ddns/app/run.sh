#!/usr/bin/with-contenv bashio
# /bin/bash bashio

#bashio::log.level "debug"

source /api_lib.sh

CERT_DIR=/data/letsencrypt

# Let's encrypt
LE_UPDATE="0"

# Config to variable
if bashio::config.has_value "ipv4"; then IPV4=$(bashio::config 'ipv4'); else IPV4="https://ipv4.text.wtfismyip.com"; fi
if bashio::config.has_value "ipv6"; then IPV6=$(bashio::config 'ipv6'); else IPV6="https://ipv6.text.wtfismyip.com"; fi
DYNU_TOKEN=$(bashio::config 'dynu_token')
DUCK_TOKEN=$(bashio::config 'duck_token')
DOMAINS=$(bashio::config 'domains')
ALIASES=$(bashio::config 'aliases')
WAIT_TIME=$(bashio::config 'seconds')

export Dynu_Token=$DYNU_TOKEN
export Duck_Token=$DUCK_TOKEN
bashio::log.debug "Dynu Token:" "$Dynu_Token"
bashio::log.debug "DuckDNS Token:" "$Duck_Token"

# Function to get the public IP
function get_public_ip() {
  # If IP is not configured manually get the public ip using wtfismyip.com
  [[ ${IPV4} != *:/* ]] && ipv4=${IPV4} || ipv4=$(curl -s -f -m 10 "${IPV4}") || true
  [[ ${IPV6} != *:/* ]] && ipv6=${IPV6} || ipv6=$(curl -s -f -m 10 "${IPV6}") || true
}

# Function that performe a renew
function le_renew() {
    local domain_args=()
    local aliases=''

    # Prepare domain for Let's Encrypt
    for domain in ${DOMAINS}; do
        for alias in $(jq --raw-output --exit-status "[.aliases[]|{(.alias):.domain}]|add.\"${domain}\" | select(. != null)" /data/options.json) ; do
            aliases="${aliases} ${alias}"
        done
    done

    aliases="$(echo "${aliases}" | tr ' ' '\n' | sort | uniq)"

    bashio::log.info "Renew certificate for domains: $(echo -n "${DOMAINS}") and aliases: $(echo -n "${aliases}")"
    for domain in $(echo "${DOMAINS}" "${aliases}" | tr ' ' '\n' | sort | uniq); do
        domain_args+=("--domain" "${domain}")
    done
    bashio::log.debug "domain_args:" "${domain_args[@]}"

    certbot certonly --force-renewal --manual --preferred-challenges dns --cert-name hass-cert \
      --manual-auth-hook /auth_script.sh \
      --manual-cleanup-hook /cleanup_script.sh \
      --register-unsafely-without-email --agree-tos \
      --deploy-hook /deploy_hook.sh \
      ${domain_args[@]}
    LE_UPDATE="$(date +%s)"
}

########################
# main                 #
########################
# Get the current public ip
get_public_ip
bashio::log.info "ipv4:" "$ipv4"
bashio::log.info "ipv6:" "$ipv6"

# Register/generate certificate if terms accepted
#if bashio::config.true 'lets_encrypt.accept_terms'; then
if true; then
# Init folder structs
    bashio::log.info "Create ${CERT_DIR}..."
    mkdir -p "${CERT_DIR}"

    # Generate new certs config
    if [ ! -d "${CERT_DIR}/live" ]; then
        bashio::log.info "Generate basic config in ${CERT_DIR}..."
        certbot certonly --non-interactive \
            --register-unsafely-without-email --agree-tos \
            -d yourdomain.com &> /dev/null || true
    fi
fi

# Loop to update the DDNS with public ip periodically.
while true; do
  get_public_ip

  bashio::log.debug "ipv4:" "$ipv4"
  bashio::log.debug "ipv6:" "$ipv6"

  for domain in ${DOMAINS}; do
    if [[ $domain == *"duckdns.org" ]]; then
      bashio::log.debug "Updating IP for DuckDNS domain:" "${domain}"

      # Update DuckDNS domain IP
      duck_ip_resp=$(curl -s "https://www.duckdns.org/update?domains=${domain}&token=${Duck_Token}&ip=${ipv4}")
      bashio::log.debug "DuckDNS IP Update response for domain ${domain}:" "${duck_ip_resp}"
    else
      # Any other domain will be considered as dynu domain
      bashio::log.debug "Updating IP for Dynu domain:" "${domain}"

      # Getting the Dynu Domain ID for the given
      DynuDomainId=$(curl -s -X GET https://api.dynu.com/v2/dns -H "accept: application/json" -H \
        "API-Key: ${Dynu_Token}"  | jq --arg domain "${domain}" '.domains[] | select(.name == $domain) | .id')
      bashio::log.debug "Dynu ${domain} ID:" "${DynuDomainId}"

      # Update the Dynu domain with the public ip
      dynu_ip_resp=$(curl -s -X POST -H "API-Key: ${Dynu_Token}" -H "Content-Type: application/json" \
        "https://api.dynu.com/v2/dns/${DynuDomainId}"  \
        -d "{\"name\":\"$domain\",\"ipv4Address\": \"${ipv4}\",\"ipv6Address\": \"${ipv6}\"}")
      bashio::log.debug "Dynu IP Update response for domain ${domain}:" "${dynu_ip_resp}"
    fi
  done
  now="$(date +%s)"
  bashio::log.debug "Time Now:" "${now}"
  bashio::log.debug "Last Update was at:" "${LE_UPDATE}"
  if bashio::config.true 'lets_encrypt.accept_terms' && [ $((now - LE_UPDATE)) -ge 432000 ]; then
    bashio::log.debug "Time to update the certificates..."
    le_renew
  fi

  bashio::log.debug "Sleep for:" "${WAIT_TIME} Sec"
  sleep "${WAIT_TIME}"
done