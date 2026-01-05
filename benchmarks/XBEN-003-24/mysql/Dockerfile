FROM mysql:5.7.15

ENV MYSQL_ROOT_PASSWORD=idor_custom_authn_header_trading_platform
ENV MYSQL_DATABASE=database

EXPOSE 3306

# Health check for K8s readiness/liveness probes
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD mysqladmin ping -h localhost -u root -p$MYSQL_ROOT_PASSWORD || exit 1
