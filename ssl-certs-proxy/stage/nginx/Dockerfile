FROM nginx:latest

RUN apt-get update
RUN apt-get install openssl inotify-tools
RUN apt-get install bash


COPY local.conf default.conf /etc/nginx/conf.d/
COPY gzip.conf options-ssl-nginx.conf hsts.conf /etc/nginx/includes/

RUN echo $(ls -a /etc/nginx/conf.d/)
RUN echo $(ls -a /etc/nginx/includes/)

COPY nginx.sh /configuration/

RUN chmod +x /configuration/nginx.sh

EXPOSE 80

CMD ["/configuration/nginx.sh"]
