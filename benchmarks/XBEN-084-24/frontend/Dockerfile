FROM node:20-alpine

RUN apk --no-cache add curl

WORKDIR /app
COPY . .
RUN npm install 
RUN npm run build
EXPOSE 3000

CMD ["npm", "start"]
