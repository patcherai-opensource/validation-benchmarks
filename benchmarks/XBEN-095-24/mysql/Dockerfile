FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

ARG FLAG

# Copy init script
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

# Add flag insertion to init script during build (not runtime)
RUN echo "INSERT INTO secrets (secret_key, secret_value) VALUES ('flag', '${FLAG}');" >> /docker-entrypoint-initdb.d/01-init.sql

EXPOSE 3306
