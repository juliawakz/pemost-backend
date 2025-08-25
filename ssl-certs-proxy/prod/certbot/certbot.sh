#!/bin/bash

set -e

export DOMAINS="georesearch.co.ke"
export CERTBOT_EMAILS="juliawakaba53@gmail.com"
export CERTBOT_TEST_CERT=0
export CERTBOT_RSA_KEY_SIZE=4096

trap exit INT TERM

if [ -z "$DOMAINS" ]; then
  echo "DOMAINS environment variable is not set"
  exit 1;
fi

until nc -z nginx 80; do
  echo "Waiting for nginx to start..."
  sleep 5s & wait ${!}
done

if [ "$CERTBOT_TEST_CERT" != "0" ]; then
  test_cert_arg="--test-cert"
fi

domain="${DOMAINS}"

if [ -d "/etc/letsencrypt/live/$domain" ]; then
  echo "Let's Encrypt certificate for $domain already exists"
  continue
fi

echo "Obtaining the certificate for $domain"

if [ -z "$CERTBOT_EMAILS" ]; then
  email_arg="--register-unsafely-without-email"
else
  email_arg="--email $CERTBOT_EMAILS"
fi

certbot certonly \
  --webroot \
  -w "/var/www/certbot/" \
  -d "pemost.$domain","model.pemost.$domain","api.pemost.$domain" \
  $test_cert_arg \
  $email_arg \
  --rsa-key-size "${CERTBOT_RSA_KEY_SIZE:-4096}" \
  --agree-tos \
  --noninteractive || true

tail -f /dev/null
