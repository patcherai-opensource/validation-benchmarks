FROM php:5-apache

WORKDIR /var/www/html
COPY . .

ARG FLAG

# Support both build-time and runtime flag injection
RUN sed -i 's/@FLAG@/'${FLAG:-'@FLAG@'}'/g' index.php

EXPOSE 80

# Default environment variable
ENV FLAG="@FLAG@"
