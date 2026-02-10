FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=builder /app/target/admin-server-1.0-SNAPSHOT.jar /app/app.jar

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create templates directory
RUN mkdir -p /tmp/templates

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
