FROM wordpress:latest
COPY . /var/www/html

# Accept flag as build argument and write to file at build time
ARG FLAG
RUN echo "${FLAG}" > /opt/flag.txt && \
    chmod 644 /opt/flag.txt

RUN chown -R www-data:www-data /var/www/html

# Standard WordPress entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["apache2-foreground"]
