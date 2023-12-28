#!/usr/bin/with-contenv bashio

#bashio::log.level "debug"

cp -f /etc/letsencrypt/live/hass-cert/fullchain.pem /ssl
cp -f /etc/letsencrypt/live/hass-cert/privkey.pem /ssl