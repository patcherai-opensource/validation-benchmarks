# Salt Top File
# This file defines which states should be applied to which minions

base:
  '*':
    - common
    - users
  
  'web*':
    - nginx
    - php
  
  'db*':
    - mysql
    - backup
