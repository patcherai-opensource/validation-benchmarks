FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=easyappointments
ENV MYSQL_DATABASE=database

EXPOSE 3306

# Add health check for Kubernetes
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD mysqladmin ping -h localhost --password=easyappointments -u root || exit 1
