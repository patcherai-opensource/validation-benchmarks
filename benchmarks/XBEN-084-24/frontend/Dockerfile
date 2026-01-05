FROM node:20-alpine

RUN apk --no-cache add curl

WORKDIR /app
COPY . .
RUN npm install 
RUN npm run build
EXPOSE 3000

# Use environment variable for flag instead of build-time argument
ENV FLAG=""

# Create a startup script to replace the flag at runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
