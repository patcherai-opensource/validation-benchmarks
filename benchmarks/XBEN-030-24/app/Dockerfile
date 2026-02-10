FROM node:20-slim

# Install git for plugin installation
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Create data and plugin directories
RUN mkdir -p /app/data /app/installed_plugins /app/temp

# Accept FLAG as build argument and write to file
ARG FLAG
RUN if [ -n "$FLAG" ]; then echo "$FLAG" > /opt/flag.txt && chmod 644 /opt/flag.txt; fi

# Set proper permissions - node user needs write access to data dirs
RUN chown -R node:node /app

# Configure git for node user
RUN git config --global user.email "admin@pluginmanager.local" && \
    git config --global user.name "Plugin Manager"

EXPOSE 3000

CMD ["node", "server.js"]
