FROM swaggerapi/swagger-ui:v3.13.2

ENV API_URLS="[{url:'http://localhost:8080/api/v1/apispec', name:'webapp'},{url:'http://localhost:8081/api/v1/apispec', name:'reposcan'}]"

RUN chmod g+w,o+w /etc/nginx/ /usr/share/nginx/html/ /var/log/nginx/ /run/nginx/ \
    && chmod o+rx /var/lib/nginx/ \
    && chmod g+rwx,o+rwx /var/lib/nginx/tmp/

