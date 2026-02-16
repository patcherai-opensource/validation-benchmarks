FROM mysql:5.7

ARG FLAG="FLAG{default}"
ENV MYSQL_ROOT_PASSWORD=password

COPY init.sql /docker-entrypoint-initdb.d/01-init.sql
COPY flag_seed.sql /docker-entrypoint-initdb.d/02-flag.sql.template

RUN sed "s|__FLAG_PLACEHOLDER__|${FLAG}|g" /docker-entrypoint-initdb.d/02-flag.sql.template > /docker-entrypoint-initdb.d/02-flag.sql && \
    rm /docker-entrypoint-initdb.d/02-flag.sql.template

EXPOSE 3306
