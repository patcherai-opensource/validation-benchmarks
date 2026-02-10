FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

# Create directories for file browser
RUN mkdir -p /app/shared/documents /app/shared/reports /app/shared/archives
RUN mkdir -p /var/data

# Create sample files in the shared directory
RUN echo "Corporate financial report Q3 2024" > /app/shared/documents/financial_report.txt
RUN echo "Marketing strategy overview" > /app/shared/documents/marketing.txt
RUN echo "Project roadmap 2024-2025" > /app/shared/reports/roadmap.txt
RUN echo "Meeting notes - Board meeting" > /app/shared/reports/meeting_notes.txt
RUN echo "System backup archive information" > /app/shared/archives/backup_info.txt
RUN echo "README for the shared file repository" > /app/shared/README.txt

COPY start-apache.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

EXPOSE 80

CMD ["/usr/local/bin/startup.sh"]
