FROM maven:3.8.4-openjdk-11-slim AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B 2>/dev/null || true

COPY src ./src

RUN mvn package -DskipTests -q

FROM tomcat:9-jdk11-openjdk-slim

# Remove default webapps
RUN rm -rf /usr/local/tomcat/webapps/*

COPY --from=builder /app/target/ROOT.war /usr/local/tomcat/webapps/ROOT.war

RUN apt-get update -y && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Accept flag at build time and plant it
ARG FLAG
RUN printf '%s' "${FLAG}" > /tmp/flag && chmod 644 /tmp/flag

# Remove server info disclosure
RUN sed -i 's/shutdown="SHUTDOWN"/shutdown="SHUTDOWN" server=""/g' /usr/local/tomcat/conf/server.xml

# JVM configuration for bean introspection across module boundaries
ENV CATALINA_OPTS="--illegal-access=permit --add-opens java.base/java.lang=ALL-UNNAMED"

EXPOSE 8080

CMD ["catalina.sh", "run"]
