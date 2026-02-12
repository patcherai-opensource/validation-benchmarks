nginx:
  pkg.installed: []
  service.running:
    - enable: True
    - watch:
      - file: /etc/nginx/nginx.conf

nginx_config:
  file.managed:
    - name: /etc/nginx/nginx.conf
    - source: salt://nginx/files/nginx.conf
    - user: root
    - group: root
    - mode: 644
