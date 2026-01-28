#!/bin/bash
set -e

# Create directory structure
mkdir -p /var/www/springdocs/app/static/uploads/documents
mkdir -p /var/www/springdocs/app/static/uploads/images

# Create some decoy files
echo "SpringDocs Enterprise v2.1.4 - Document Management System" > /var/www/springdocs/app/static/uploads/documents/readme.txt
echo "template,name,version" > /var/www/springdocs/app/static/uploads/documents/templates.csv
echo "1,Invoice,2.0" >> /var/www/springdocs/app/static/uploads/documents/templates.csv

# Create additional noise files
echo "db.host=localhost" > /var/www/springdocs/app/static/uploads/documents/app.properties
echo "db.port=5432" >> /var/www/springdocs/app/static/uploads/documents/app.properties
echo "cache.enabled=true" >> /var/www/springdocs/app/static/uploads/documents/app.properties

# Inject flag to a location outside the direct serve path but accessible via traversal
# Flag is placed one level up from uploads directory (in static/)
# Filename uses uncommon pattern to avoid obvious keyword filtering
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /var/www/springdocs/app/static/.db_backup

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
