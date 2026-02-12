app_directory:
  file.directory:
    - name: /opt/app
    - user: deploy
    - group: deploy
    - mode: 755

app_virtualenv:
  virtualenv.managed:
    - name: /opt/app/venv
    - python: /usr/bin/python3
    - user: deploy
    - require:
      - file: app_directory

app_service:
  file.managed:
    - name: /etc/systemd/system/app.service
    - source: salt://deploy/files/app.service
    - user: root
    - group: root
    - mode: 644
  service.running:
    - name: app
    - enable: True
    - require:
      - file: app_service
