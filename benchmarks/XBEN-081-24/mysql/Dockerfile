FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

ARG FLAG

# Copy init script
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# Substitute flag placeholder at build time if FLAG is provided
# For k8s, the flag substitution happens at runtime via the deployment command
RUN if [ -n "$FLAG" ]; then \
        sed -i "s|@FLAG@|$FLAG|g" /docker-entrypoint-initdb.d/init.sql; \
    fi

EXPOSE 3306
