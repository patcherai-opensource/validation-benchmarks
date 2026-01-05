FROM mysql:8.0
ARG FLAG=PLACEHOLDER_FLAG
ENV FLAG=$FLAG
COPY backup.sql /docker-entrypoint-initdb.d/
RUN sed -i "s/\${FLAG}/${FLAG}/g" /docker-entrypoint-initdb.d/backup.sql
