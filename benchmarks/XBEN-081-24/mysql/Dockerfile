FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

# Save original entrypoint before overwriting
RUN cp /usr/local/bin/docker-entrypoint.sh /usr/local/bin/original-entrypoint.sh

# Copy init script that will handle flag substitution at runtime
COPY init.sql /docker-entrypoint-initdb.d/init-template.sql
COPY docker-entrypoint.sh /usr/local/bin/custom-entrypoint.sh

RUN chmod +x /usr/local/bin/custom-entrypoint.sh /usr/local/bin/original-entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
CMD ["mysqld"]
