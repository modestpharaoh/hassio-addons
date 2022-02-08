#!/bin/sh
gunicorn --chdir /app remoteSpeaker:app -w 1 --threads 2 -b 0.0.0.0:5005 --log-file=- --limit-request-line 0
