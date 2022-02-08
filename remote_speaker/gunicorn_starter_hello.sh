#!/bin/sh
gunicorn --chdir /app hello_world:app -w 2 --threads 2 -b 0.0.0.0:5004
