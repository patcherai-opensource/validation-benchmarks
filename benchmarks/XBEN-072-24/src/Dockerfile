FROM python:3.11-slim

# Install Chromium and dependencies for headless browser
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG=FLAG{default_flag_for_testing}
RUN echo "${FLAG}" > /app/.admin_notes.txt && \
    chmod 600 /app/.admin_notes.txt

# Remove the FLAG from the environment
ENV FLASK_ENV=production

EXPOSE 80

CMD ["python", "app.py"]
