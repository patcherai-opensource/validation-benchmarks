base:
  '*':
    - common
    - users
  'web-*':
    - nginx
    - certbot
  'db-*':
    - postgresql
    - backup
  'app-*':
    - python
    - deploy
