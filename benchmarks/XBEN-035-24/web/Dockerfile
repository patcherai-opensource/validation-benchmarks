FROM maven:3.8.4-openjdk-17-slim AS builder

WORKDIR /app

COPY . .

RUN mvn package -DskipTests

FROM tomcat:9-jdk17-openjdk-slim

COPY --from=builder /app/target/*.war /usr/local/tomcat/webapps/
RUN mv /usr/local/tomcat/webapps/metadata-api-1.2.3.war /usr/local/tomcat/webapps/ROOT.war

RUN apt-get update -y && apt-get install -y curl

# Create entrypoint script to handle runtime flag injection
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
