# Common state file
# Applied to all minions

packages:
  pkg.installed:
    - pkgs:
      - vim
      - curl
      - wget
      - htop

/etc/timezone:
  file.managed:
    - contents: |
        UTC
    - user: root
    - group: root
    - mode: 644
