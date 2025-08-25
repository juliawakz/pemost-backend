FROM certbot/certbot:v1.27.0

RUN apk add --no-cache bash

COPY certbot.sh /opt/

RUN mkdir -p /var/www/certbot

RUN chmod +x /opt/certbot.sh

ENTRYPOINT ["/opt/certbot.sh"]
