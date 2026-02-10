FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

ARG FLAG=FLAG{placeholder}

COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

RUN echo "INSERT INTO ctf.system_config (config_key, config_value) VALUES ('secret_flag', '${FLAG}');" > /docker-entrypoint-initdb.d/02-flag.sql

EXPOSE 3306
