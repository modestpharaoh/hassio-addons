#!/usr/bin/env bashio

# bashio::log.level "debug"

bashio::log.info "Deploying new certs to /ssl ..."
cp -f /etc/letsencrypt/live/hass-cert/fullchain.pem /ssl
cp -f /etc/letsencrypt/live/hass-cert/privkey.pem /ssl
bashio::log.info "Certificates Deployed!"
