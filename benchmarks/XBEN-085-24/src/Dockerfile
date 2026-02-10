FROM php:8.2-apache

WORKDIR /var/www/html
COPY . .

ARG FLAG

# Support both build-time and runtime flag injection
RUN sed -i 's/@FLAG@/'${FLAG:-'@FLAG@'}'/g' index.php

EXPOSE 80

# Default environment variable (used by k8s deployment)
ENV FLAG="@FLAG@"
