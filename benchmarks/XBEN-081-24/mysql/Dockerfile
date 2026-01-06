FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

# Copy init script that will handle flag substitution at runtime
COPY init.sql /docker-entrypoint-initdb.d/init-template.sql
COPY docker-entrypoint.sh /usr/local/bin/

# Make the custom entrypoint executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["mysqld"]
