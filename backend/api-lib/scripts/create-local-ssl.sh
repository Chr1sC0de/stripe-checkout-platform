#! /bin/bash
: '
This script is used to create the local ssl certificates required to
run the fastapi locally using https
'

openssl \
    req \
    -x509 \
    -newkey rsa:4096 \
    -nodes \
    -out cert.pem \
    -keyout key.pem \
    -days 365 \
    -subj "/C=AU/ST=Victoria/L=Melbourne/O=[]/OU=[]/CN=0.0.0.0" \
    -addext "subjectAltName = DNS:foobar.mydomain.svc"