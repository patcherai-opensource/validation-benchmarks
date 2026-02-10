# User management state

admin_user:
  user.present:
    - name: admin
    - shell: /bin/bash
    - home: /home/admin
    - groups:
      - sudo
      - admin

deploy_user:
  user.present:
    - name: deploy
    - shell: /bin/bash
    - home: /home/deploy
