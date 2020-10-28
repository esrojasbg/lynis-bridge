#!/bin/sh

if [[ -z "${SSL}" ]]; then
    # SSL was not requested
    gunicorn -w 5 --bind 0.0.0.0:8080 main:app
else
    if [ ! -f /opt/key.pem ]; then
        # SSL was requested, but not server.key was provided
        # create self-signed
        openssl req -x509 -newkey rsa:4096 -keyout key.pem \
            -out cert.pem -days 365 -nodes -subj "/C=EU/ST=EU/L=EU/O=lynis/CN=lynis-bridge"
    fi
    # SSL was requested with a server.key
    gunicorn -w 5 --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:8080 main:app
fi






