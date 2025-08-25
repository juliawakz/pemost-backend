#!/bin/sh
echo "Renewing Let's Encrypt Certificates... (`date`)"
docker exec certbot certbot renew --no-random-sleep-on-renew
echo "Reloading Nginx configuration"
docker exec nginx nginx -s reload