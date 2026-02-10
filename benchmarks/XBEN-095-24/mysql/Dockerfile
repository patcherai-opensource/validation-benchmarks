FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

EXPOSE 3306
