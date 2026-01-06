FROM mysql:5.7.15

ENV MYSQL_ROOT_PASSWORD=ssti_loan_calculator
ENV MYSQL_DATABASE=database

EXPOSE 3306

# Add health check for Kubernetes
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD mysqladmin ping -h localhost --password=ssti_loan_calculator -u root || exit 1
