FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a startup script to handle flag injection at runtime
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

CMD ["/startup.sh"]

EXPOSE 5000
