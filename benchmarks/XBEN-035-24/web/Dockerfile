FROM maven:3.8.4-openjdk-17-slim AS builder

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn package -DskipTests -q

FROM eclipse-temurin:17-jre-alpine

RUN apk add --no-cache curl bash

WORKDIR /app

COPY --from=builder /app/target/admin-server-1.0.0.jar app.jar

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
