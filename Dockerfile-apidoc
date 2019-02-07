FROM swaggerapi/swagger-ui:v3.13.2

RUN chmod g+w,o+w /etc/nginx/ /usr/share/nginx/html/ /var/log/nginx/ /run/nginx/ \
    && chmod o+rx /var/lib/nginx/ \
    && chmod g+rwx,o+rwx /var/lib/nginx/tmp/
