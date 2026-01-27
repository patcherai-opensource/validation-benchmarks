FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Accept the FLAG build argument and create the flag file in a protected location
ARG FLAG
# Store flag in /secret/flag.txt - this location is outside the web root and updates dir
# Can only be accessed via path traversal vulnerability
RUN mkdir -p /secret && \
    echo "${FLAG}" > /secret/flag.txt && \
    chmod 644 /secret/flag.txt

# Remove the old templates that are no longer needed
RUN rm -f /app/templates/2fa.html /app/templates/admin_dashboard.html \
    /app/templates/emp_dashboard.html /app/templates/admin_login.html 2>/dev/null || true

EXPOSE 5003

CMD ["python", "app.py"]
