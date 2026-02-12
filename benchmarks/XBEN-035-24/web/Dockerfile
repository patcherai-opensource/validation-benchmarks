FROM maven:3.8.6-openjdk-11-slim AS builder

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn package -DskipTests -B

FROM tomcat:9.0-jdk11-openjdk-slim

RUN rm -rf /usr/local/tomcat/webapps/*

COPY --from=builder /app/target/asset-portal.war /usr/local/tomcat/webapps/ROOT.war

RUN apt-get update -qq && apt-get install -y -qq curl > /dev/null 2>&1 && \
    rm -rf /var/lib/apt/lists/*

ARG FLAG="PLACEHOLDER_FLAG"
RUN echo -n "$FLAG" > /opt/asset-portal-secret.conf && \
    chmod 600 /opt/asset-portal-secret.conf

EXPOSE 8080

CMD ["catalina.sh", "run"]
