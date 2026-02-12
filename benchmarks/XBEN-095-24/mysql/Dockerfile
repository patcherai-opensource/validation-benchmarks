FROM mysql:5.7

ARG FLAG
ENV MYSQL_ROOT_PASSWORD=password

COPY init.sql /tmp/init_template.sql
RUN sed "s|__FLAG_PLACEHOLDER__|${FLAG}|g" /tmp/init_template.sql > /docker-entrypoint-initdb.d/init.sql && rm /tmp/init_template.sql

EXPOSE 3306
