FROM php:7.4-apache

COPY . /var/www/html/

EXPOSE 80

RUN apt-get update -y

RUN apt-get install -y curl

# Enable environment variable substitution at runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
