#!/bin/bash

ARCH=$1
BUILD_OPTIONS=$2   # --no--cache

sudo docker build ${BUILD_OPTIONS} --build-arg BUILD_FROM=$(jq -r ".build_from[\"$ARCH\"]" build.json) -t hass-multi-ddns .


echo -e "\n\nTo run the test:
  docker run -d --name test-hass-multi-ddns -v /path/to/your/config:/data:rw -p hass-multi-ddns

    Where in data dir, you should have option.json, which contains the required settings to run the docker
"



echo -e "\n\n option.json sample:
{
  "lets_encrypt": {
    "accept_terms": true,
    "certfile": "fullchain.pem",
    "keyfile": "privkey.pem"
  },
  "duck_token": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "dynu_token": "xxxxxxxxxxxxxxxxxxxxxxx",
  "domains": [
    "xxxx.dynu.org",
    "*.xxxx.dynu.org"
  ],
  "aliases": [],
  "wildcard_alias": true,
  "seconds": 300,
  "log_level": "info"
}



"
