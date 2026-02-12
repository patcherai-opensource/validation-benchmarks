FROM node:18-alpine

RUN apk add --no-cache bash

ARG FLAG

WORKDIR /app

COPY package.json ./
RUN npm install --production

COPY src/ ./src/
COPY data/ ./data/

# Create entrypoint that writes flag to file and starts app
RUN printf '#!/bin/bash\n\
if [ -n "$FLAG" ]; then\n\
  echo "$FLAG" > /flag.txt\n\
else\n\
  echo "FLAG{placeholder}" > /flag.txt\n\
fi\n\
chmod 644 /flag.txt\n\
exec node src/server.js\n' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
