FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=node_fleet_manager
ENV MYSQL_DATABASE=database

EXPOSE 3306

# Add health check for Kubernetes
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD mysqladmin ping -h localhost --password=node_fleet_manager -u root || exit 1
