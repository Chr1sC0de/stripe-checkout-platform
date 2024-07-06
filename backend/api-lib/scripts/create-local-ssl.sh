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