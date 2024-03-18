#!/usr/bin/with-contenv bashio

# Logs should include the date/time.
export __BASHIO_LOG_TIMESTAMP="%y-%m-%d %T"

if bashio::var.has_value "log_level"; then
  bashio::log.level "$(bashio::config 'log_level')"
fi

source /api_lib.sh

set +e

CERT_DIR=/data/letsencrypt

# Let's encrypt
LE_UPDATE="0"

# Config to variable
if bashio::config.has_value "ipv4"; then IPV4=$(bashio::config 'ipv4'); else IPV4="https://ipv4.text.wtfismyip.com"; fi
if bashio::config.has_value "ipv6"; then IPV6=$(bashio::config 'ipv6'); else IPV6="https://ipv6.text.wtfismyip.com"; fi
IPV4_="https://ifconfig.co/ip"
IPV6_="https://ifconfig.co/ip6"
DYNU_TOKEN=$(bashio::config 'dynu_token')
DUCK_TOKEN=$(bashio::config 'duck_token')
DOMAINS=$(bashio::config 'domains')
ALIASES=$(bashio::config 'aliases')
WAIT_TIME=$(bashio::config 'seconds')
WILDCARD=$(bashio::config 'wildcard_alias')

export Dynu_Token=$DYNU_TOKEN
export Duck_Token=$DUCK_TOKEN
bashio::log.debug "Dynu Token:" "$Dynu_Token"
bashio::log.debug "DuckDNS Token:" "$Duck_Token"
prv_ipv4=""
prv_ipv6=""

# Function to get the public IP
function get_public_ip() {
  # If IP is not configured manually get the public ip using wtfismyip.com
  [[ ${IPV4} != *:/* ]] && ipv4=${IPV4} || ipv4=$(curl -s -f -m 20 "${IPV4}") || ipv4=$(curl -s -f -m 20 "${IPV4_}") || ipv4=""
  [[ ${IPV6} != *:/* ]] && ipv6=${IPV6} || ipv6=$(curl -s -f -m 20 "${IPV6}") || ipv6=$(curl -s -f -m 20 "${IPV6_}") || ipv6=""
  bashio::log.debug "ipv4:" "$ipv4"
  bashio::log.debug "ipv6:" "$ipv6"

  if [ -z "$ipv4" ] ; then
    bashio::log.warning "Failed to get the current public IPv4!"
  else
    if [ "$ipv4" != "$prv_ipv4" ]; then
      bashio::log.info "IPv4 changed from $prv_ipv4 to $ipv4"
      prv_ipv4="$ipv4"
    fi
  fi

  if [ -z "$ipv6" ] ; then
    bashio::log.debug "Failed to get the current public IPv6!"
  else
    if [ "$ipv6" != "$prv_ipv6" ]; then
      bashio::log.info "IPv6 changed from $prv_ipv6 to $ipv6"
      prv_ipv6="$ipv6"
    fi
  fi
}

# Function to get domains in current certificate
function get_current_cert_domains() {
  cert_domains=$(openssl x509 -in /ssl/fullchain.pem -noout -text | grep -E 'DNS:' |  sed 's/DNS://g; s/ //g')
  IFS=',' read -ra cert_domains_array <<< "$cert_domains"
}

# Function to get domains that should be included in the certificate
function get_domains_arrays() {
  domain_args=()
  main_domain_args=()
  domains_array=()
  main_domains_array=()
  aliases=''
  
  for domain in ${DOMAINS}; do
      for alias in $(jq --raw-output --exit-status "[.aliases[]|{(.alias):.domain}]|add.\"${domain}\" | select(. != null)" /data/options.json) ; do
          aliases="${aliases} ${alias}"
      done
  done

  aliases="$(echo "${aliases}" | tr ' ' '\n' | sort | uniq)"

  for domain in $(echo "${DOMAINS}" "${aliases}" | tr ' ' '\n' | sort | uniq); do
    domain_args+=("--domain" "${domain}")
    domains_array+=("${domain}")
    if [[ $domain != *"*."* ]]; then
      main_domain_args+=("--domain" "${domain}")
      main_domains_array+=("${domain}")
    fi
  done

  # Getting current domains included in current certificate
  get_current_cert_domains

  bashio::log.debug "cert_domains_array:" "${cert_domains_array[@]}"
  bashio::log.debug "domains_array:" "${domains_array[@]}"
  bashio::log.debug "domain_args:" "${domain_args[@]}"
  bashio::log.debug "main_domains_array:" "${main_domains_array[@]}"
  bashio::log.debug "main_domain_args:" "${main_domain_args[@]}"
}

# Function to get the epoch time after a month
function get_month_epoch() {
  current_time=$(date +%s)
  one_month=$((current_time + 30 * 24 * 60 * 60))
}

# Function to get the expiry date of the certificate
function get_cert_expiry() {
  expiration_date=$(openssl x509 -in /ssl/fullchain.pem -noout -dates -enddate | awk -F= '/notAfter/ {print $2}' 2> /dev/null)
  if [ $? -eq 0 ]; then
    expiry_epoch=$(date -D "%b %d %H:%M:%S %Y GMT" -d "$expiration_date" +"%s")
    return 0
  fi
  expiry_epoch=0
}

# Function that performe a renew
function le_renew() {
    get_cert_expiry
    get_month_epoch
    bashio::log.debug "Certificate will expire at:" "$expiry_epoch"
    bashio::log.debug "Epoch + one month:" "$one_month"

    # Skip update, if certificate will expire more than a month 
    if [ "$expiry_epoch" -ge "$one_month" ] && [ "$domains_in_cert_match" = true ]; then
      bashio::log.debug "Certificate is valid for more than a month, Skipping certificate update!!!"
      LE_UPDATE="$(date +%s)"
      return 0
    fi
    if [ "$domains_in_cert_match" = false ]; then
      bashio::log.info "Domains in certificate are not matched!!!!!"
    fi
    if [ "$expiry_epoch" -lt "$one_month" ]; then
      bashio::log.info "Certificate will be expire in less than a month!!!!!"
    fi

    bashio::log.info "Renew certificate for domains: $(echo -n "${DOMAINS}") and aliases: $(echo -n "${aliases}")"

    bashio::log.info "Force renewal certificates for domains: ${main_domains_array[@]}"
    certbot certonly --force-renewal --manual --preferred-challenges dns --cert-name hass-cert \
      --manual-auth-hook /auth_script.sh \
      --manual-cleanup-hook /cleanup_script.sh \
      --register-unsafely-without-email --agree-tos \
      --deploy-hook /deploy_hook.sh \
      --non-interactive \
      ${main_domain_args[@]}
    renew_exit_code=$?
    

    if [ $renew_exit_code -ne 0 ]; then
      bashio::log.warning "Certbot renewal exit code:" "$renew_exit_code!!!!"
      bashio::log.warning "Skipping certificate renewal for some time!!!"
    else
      bashio::log.info "Successfully deploy certificates with base domains!"
      # If there are some domain with *, we will add them by expand
      if [ ${#domain_args[@]} -gt ${#main_domain_args[@]} ]; then
        domains_in_cert_match=false
        bashio::log.info "Expanding certificates for domains: ${domains_array[@]}"
        bashio::log.debug "Wait for 60 sec..."
        sleep 60
        certbot certonly --expand --manual --preferred-challenges dns --cert-name hass-cert \
          --manual-auth-hook /auth_script.sh \
          --manual-cleanup-hook /cleanup_script.sh \
          --register-unsafely-without-email --agree-tos \
          --deploy-hook /deploy_hook.sh \
          --non-interactive \
          ${domain_args[@]}
        if [ $? -ne 0 ]; then
          bashio::log.warning "Certbot expand exit code:" "$?"
        else
          domains_in_cert_match=true
          bashio::log.info "Successfully expanding the certificates to with sub-domains!"
        fi
      fi
    fi

    LE_UPDATE="$(date +%s)"
    bashio::log.debug "Next update at epoch:" "$LE_UPDATE"
}

########################
# main                 #
########################
# Get the current public ip
get_public_ip
bashio::log.info "ipv4:" "$ipv4"
bashio::log.info "ipv6:" "$ipv6"

# Get the domains required in the certificate
get_domains_arrays

# Check if domains are included in the current certificate or different
domains_in_cert_match=true
if [ "${#cert_domains_array[@]}" -eq "${#domains_array[@]}" ]; then
  for cert_domain in "${cert_domains_array[@]}"; do
    if [[ ! " ${domains_array[@]} " =~ " $cert_domain " ]]; then
        domains_in_cert_match=false
        break
    fi
  done
else
  domains_in_cert_match=false
fi

# remove the old certificates, if it is not matched
if [ "$domains_in_cert_match" = false ]; then
  bashio::log.warning "Domains are changed, deleting old certificates in ${CERT_DIR}!!!!"
  rm -rf ${CERT_DIR}/*

  # Register/generate certificate if terms accepted
  if bashio::config.true 'lets_encrypt.accept_terms'; then
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
else
  bashio::log.info "The current certificates in /ssl/ has the required domains!!!!"
  get_cert_expiry
  get_month_epoch
  if [ "$expiry_epoch" -ge "$one_month" ]; then
    bashio::log.info "The current certificates will be expire in more than a month, script will skip cert renewal!!!!!"
  fi
fi

# Loop to update the DDNS with public ip periodically.
while true; do
  get_public_ip

  for domain in ${DOMAINS}; do
    # Skipping any *.xxx.duckdns.org  or *.xxx.${dynu_domain}.org
    if [[ $domain != *"*."* ]]; then
      if [[ $domain == *"duckdns.org" ]]; then
        
        # Update DuckDNS domain with the public IPv4
        if [ -n "$ipv4" ] ; then
          bashio::log.debug "Domain ${domain}: Updating DuckDNS with IPv4: $ipv4"
          duck_ipv4_resp=$(curl -s -f -m 10 "https://www.duckdns.org/update?domains=${domain}&token=${Duck_Token}&ip=${ipv4}")
          bashio::log.debug "Domain ${domain}: DuckDNS update IP response:" "${duck_ipv4_resp}"
        else
          bashio::log.warning "Domain ${domain}: Skipping DuckDNS IPv4 update, as IPv4 is empty!!"
        fi

        # Update DuckDNS domain with the public IPv6
        if [ -n "$ipv6" ] ; then
          bashio::log.debug "Domain ${domain}: Updating DuckDNS with IPv6: $ipv6"
          duck_ipv6_resp=$(curl -s -f -m 10 "https://www.duckdns.org/update?domains=${domain}&token=${Duck_Token}&ipv6=${ipv6}")
          bashio::log.debug "Domain ${domain}: DuckDNS update IP response:" "${duck_ipv6_resp}"
        else
          bashio::log.debug "Domain ${domain}: Skipping DuckDNS IPv6 update, as IPv6 is empty!!"
        fi

      else
        if [ -n "$ipv4" ] || [ -n "$ipv6" ] ; then
          # Any other domain will be considered as dynu domain
          bashio::log.debug "Domain ${domain}: Updating DuckDNS with IPv4: $ipv4 & IPv6: $ipv6"

          # Getting the Dynu Domain ID
          DynuDomainId=$(get_dynu_domain_id $domain $Dynu_Token)
          if [ $? -eq 0 ]; then
            # Update the Dynu domain with the public ip
            dynu_ip_resp=$(curl -s -f -m 20 -X POST -H "API-Key: ${Dynu_Token}" -H "Content-Type: application/json" \
              "https://api.dynu.com/v2/dns/${DynuDomainId}"  \
              -d "{\"name\":\"$domain\",\"ipv4Address\": \"${ipv4}\",\"ipv6Address\": \"${ipv6}\",\"ipv4WildcardAlias\": ${WILDCARD},\"ipv6WildcardAlias\": ${WILDCARD}}")
            bashio::log.debug "Domain ${domain}: Dynu update ip response:" "${dynu_ip_resp}"
          else
            bashio::log.warning "Domain ${domain}: Skipping Dynu IP update, as failed to get Dynu domain ID!!"
          fi
        else
          bashio::log.debug "Domain ${domain}: Skipping Dynu IP update, as IPv4 & IPv6 are empty!!"
        fi
      fi
    fi
  done
  now="$(date +%s)"
  bashio::log.debug "Time Now:" "${now}"
  bashio::log.debug "Last Update was at:" "${LE_UPDATE}"
  if bashio::config.true 'lets_encrypt.accept_terms' && [ $((now - LE_UPDATE)) -ge 43200 ]; then
    bashio::log.debug "Time to update the certificates..."
    le_renew
  fi

  bashio::log.debug "Sleep for:" "${WAIT_TIME} Sec"
  sleep "${WAIT_TIME}"
done