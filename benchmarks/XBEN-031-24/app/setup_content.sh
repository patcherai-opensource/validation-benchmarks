#!/bin/bash
# Initialize content roots and sample managed files
set -e

# Create content root directories
mkdir -p /srv/conductor/content/production
mkdir -p /srv/conductor/content/staging
mkdir -p /var/cache/conductor
mkdir -p /var/log/conductor

# Production environment files
cat > /srv/conductor/content/production/nginx.conf <<'CONF'
worker_processes auto;
events {
    worker_connections 1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile      on;
    keepalive_timeout 65;

    server {
        listen 80;
        server_name localhost;
        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }
    }
}
CONF

cat > /srv/conductor/content/production/motd <<'MOTD'
###############################################
#  Managed by Conductor - Do not edit manually  #
#  Environment: production                      #
###############################################
MOTD

cat > /srv/conductor/content/production/sysctl.conf <<'SYSCTL'
# Kernel parameters managed by Conductor
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
vm.swappiness = 10
fs.file-max = 65536
SYSCTL

cat > /srv/conductor/content/production/resolv.conf <<'RESOLV'
nameserver 10.0.0.2
nameserver 10.0.0.3
search internal.corp
RESOLV

mkdir -p /srv/conductor/content/production/scripts
cat > /srv/conductor/content/production/scripts/health_check.sh <<'SCRIPT'
#!/bin/bash
# Node health check script
curl -sf http://localhost/ping > /dev/null 2>&1
exit $?
SCRIPT

cat > /srv/conductor/content/production/conductor.yaml <<'YAML'
# Conductor node configuration
# Distributed to managed nodes via the content distribution API
master_host: conductor-master.internal.corp
master_port: 8080
auth:
  # Nodes authenticate using the master key stored at /etc/conductor/master.key
  method: key
  key_path: /etc/conductor/master.key
  verify_ssl: true
content_env: production
log_level: info
cache_dir: /var/cache/conductor
retry_interval: 30
YAML

# Staging environment files
cat > /srv/conductor/content/staging/nginx.conf <<'CONF'
worker_processes 2;
events {
    worker_connections 512;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile      on;

    server {
        listen 80;
        server_name staging.local;
        location / {
            root   /usr/share/nginx/html;
        }
    }
}
CONF

cat > /srv/conductor/content/staging/motd <<'MOTD'
###############################################
#  STAGING ENVIRONMENT                          #
#  Managed by Conductor                         #
###############################################
MOTD
