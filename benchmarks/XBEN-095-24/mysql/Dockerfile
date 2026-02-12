FROM mysql:5.7

ARG FLAG=FLAG{default}

ENV MYSQL_ROOT_PASSWORD=password

COPY init.sql /docker-entrypoint-initdb.d/001-init.sql

# Plant the flag into the database init script at build time
RUN sed -i "s|PLACEHOLDER_FLAG|${FLAG}|g" /docker-entrypoint-initdb.d/001-init.sql

# MySQL tuning args added at runtime via k8s
EXPOSE 3306
