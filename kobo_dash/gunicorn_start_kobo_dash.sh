#!/bin/bash
gunicorn --chdir /app draw-hass-dash-service:app -w 1 --threads 2 -b 0.0.0.0:5006 --log-file=- --limit-request-line 0
