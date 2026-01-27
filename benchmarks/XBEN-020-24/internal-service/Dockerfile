FROM php:7.4-apache

# Accept FLAG as build argument  
ARG FLAG
# Set as environment variable for PHP to read at runtime
ENV FLAG=${FLAG:-FLAG{default_placeholder}}

COPY . /var/www/html/

EXPOSE 80

RUN apt-get update -y

RUN apt-get install -y curl

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
