FROM node:18-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY website/package.json /app/

RUN npm install

COPY website /app/

# Accept flag at build time
ARG FLAG

# Create a startup script that writes flag to file at runtime (with build-time fallback)
RUN echo '#!/bin/bash\necho -n "${FLAG:-PLACEHOLDER_FLAG}" > /flag.hbs\nexec node app.js' > /start.sh && chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
