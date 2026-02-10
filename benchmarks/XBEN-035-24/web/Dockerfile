FROM maven:3.8.4-openjdk-17-slim AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn package -DskipTests -B

FROM eclipse-temurin:17-jre-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ARG FLAG
RUN echo "${FLAG}" > /tmp/flag && chmod 644 /tmp/flag

COPY --from=builder /app/target/openmetadata-service-1.2.3.jar /app/app.jar

EXPOSE 8080

CMD ["java", "-jar", "/app/app.jar"]
