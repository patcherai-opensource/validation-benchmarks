deploy_user:
  user.present:
    - name: deploy
    - shell: /bin/bash
    - home: /home/deploy
    - groups:
      - sudo
      - docker

deploy_ssh_key:
  ssh_auth.present:
    - user: deploy
    - source: salt://users/files/deploy.pub
    - enc: ssh-rsa

ops_user:
  user.present:
    - name: ops
    - shell: /bin/bash
    - home: /home/ops
    - groups:
      - sudo
