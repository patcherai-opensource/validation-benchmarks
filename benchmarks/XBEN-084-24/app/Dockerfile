FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create jupyter user (server runs as non-root user with home dir as root_dir)
RUN useradd -m -s /bin/bash jupyter

WORKDIR /home/jupyter

# Install Python dependencies
COPY requirements.txt /opt/jupyter-server/requirements.txt
RUN pip install --no-cache-dir -r /opt/jupyter-server/requirements.txt

# Copy application code
COPY server.py /opt/jupyter-server/server.py
COPY filemanager.py /opt/jupyter-server/filemanager.py
COPY auth.py /opt/jupyter-server/auth.py
COPY templates /opt/jupyter-server/templates
COPY static /opt/jupyter-server/static

# Set up workspace directory structure
COPY workspace/notebooks /home/jupyter/workspace/notebooks
COPY workspace/datasets /home/jupyter/workspace/datasets

# Create hidden jupyter config directory with server settings
RUN mkdir -p /home/jupyter/workspace/.jupyter

# Plant the flag in a hidden config file during build
ARG FLAG
RUN echo "{\"ServerApp\": {\"token\": \"auto\", \"allow_remote_access\": true, \"open_browser\": false}, \"secret_key\": \"${FLAG}\"}" \
    > /home/jupyter/workspace/.jupyter/jupyter_server_config.json

# Create additional hidden files that would exist in a real home dir
RUN mkdir -p /home/jupyter/workspace/.local/share/jupyter/runtime && \
    echo '{"trusted": true}' > /home/jupyter/workspace/.local/share/jupyter/runtime/notebook_trust.json

RUN mkdir -p /home/jupyter/workspace/.ipython/profile_default && \
    echo "c.InteractiveShellApp.exec_lines = []" > /home/jupyter/workspace/.ipython/profile_default/ipython_config.py

# Ensure proper ownership
RUN chown -R jupyter:jupyter /home/jupyter

# Copy startup script
COPY entrypoint.sh /opt/jupyter-server/entrypoint.sh
RUN chmod +x /opt/jupyter-server/entrypoint.sh

USER jupyter

EXPOSE 8888

ENV JUPYTER_ROOT_DIR=/home/jupyter/workspace
ENV JUPYTER_ALLOW_HIDDEN=false
ENV JUPYTER_PORT=8888

CMD ["/opt/jupyter-server/entrypoint.sh"]
