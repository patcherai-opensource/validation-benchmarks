FROM mysql:8.0

ARG FLAG
ENV MYSQL_ROOT_PASSWORD=contentflow_db
ENV MYSQL_DATABASE=contentflow

COPY init.sql /tmp/init_template.sql

# Replace flag placeholder with actual flag at build time, then place in init directory
RUN sed "s/@FLAG@/${FLAG}/g" /tmp/init_template.sql > /docker-entrypoint-initdb.d/01-init.sql && \
    rm /tmp/init_template.sql

EXPOSE 3306