FROM mysql:8.0

# Copy the database initialization
COPY backup.sql /docker-entrypoint-initdb.d/init.sql

# Add custom MySQL configuration for K8s compatibility
RUN echo '[mysqld]\n\
bind-address = 0.0.0.0\n\
port = 3306\n\
default-authentication-plugin=mysql_native_password\n' > /etc/mysql/conf.d/k8s.cnf

EXPOSE 3306
