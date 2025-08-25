FROM alpine:3.15

RUN apk update && \
    apk add --no-cache docker-cli

COPY cert_renew.sh /etc/periodic/daily/renew_certs

RUN chmod +x /etc/periodic/daily/renew_certs

WORKDIR /workdir

CMD ["crond", "-f", "-L", "/dev/stdout"]

#ENTRYPOINT tail -f /dev/null