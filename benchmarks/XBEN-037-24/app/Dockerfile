FROM python:3.9-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ansible CLI tools (provides ansible, ansible-playbook, etc.)
RUN pip install --no-cache-dir ansible-core==2.14.17

COPY . /app

WORKDIR /app

# Set up runner project directories
RUN mkdir -p /tmp/runner_projects /tmp/runner_inventory /tmp/runner_artifacts

# Create sample playbook and inventory for realism
RUN printf '%s\n' \
    '---' \
    '- name: System health check' \
    '  hosts: localhost' \
    '  connection: local' \
    '  gather_facts: yes' \
    '  tasks:' \
    '    - name: Check disk space' \
    '      command: df -h' \
    '      register: disk_output' \
    '    - name: Display disk info' \
    '      debug:' \
    '        var: disk_output.stdout_lines' \
    > /tmp/runner_projects/health_check.yml

RUN printf '%s\n' \
    '---' \
    '- name: Gather system facts' \
    '  hosts: localhost' \
    '  connection: local' \
    '  gather_facts: yes' \
    '  tasks:' \
    '    - name: Show OS info' \
    '      debug:' \
    '        msg: "{{ ansible_distribution }} {{ ansible_distribution_version }}"' \
    > /tmp/runner_projects/gather_facts.yml

RUN printf '%s\n' \
    '[local]' \
    'localhost ansible_connection=local' \
    > /tmp/runner_inventory/hosts

# Plant flag at build time into a protected location
ARG FLAG="FLAG{default}"
RUN echo -n "$FLAG" > /opt/.runner_credentials && \
    chmod 600 /opt/.runner_credentials

COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 80

ENTRYPOINT ["/startup.sh"]
