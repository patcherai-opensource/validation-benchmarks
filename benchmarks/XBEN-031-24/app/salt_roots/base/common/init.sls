common_packages:
  pkg.installed:
    - pkgs:
      - vim
      - curl
      - wget
      - htop
      - tmux
      - git

timezone_set:
  timezone.system:
    - name: UTC

ntp_service:
  service.running:
    - name: chrony
    - enable: True

sysctl_tuning:
  sysctl.present:
    - name: net.core.somaxconn
    - value: 65535

logrotate_config:
  file.managed:
    - name: /etc/logrotate.d/salt
    - contents: |
        /var/log/salt/* {
            weekly
            missingok
            rotate 12
            compress
            notifempty
        }
