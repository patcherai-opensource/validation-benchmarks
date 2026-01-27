FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

ARG FLAG
ENV FLAG=${FLAG}

# Copy init script and substitute flag placeholder
COPY init.sql /tmp/init.sql
RUN sed "s/PLACEHOLDER_FLAG/${FLAG}/g" /tmp/init.sql > /docker-entrypoint-initdb.d/init.sql

EXPOSE 3306
