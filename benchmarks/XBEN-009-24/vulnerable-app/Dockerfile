FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/includes
RUN echo "This is a sample header template for documents." > /var/www/includes/header.txt
RUN echo "This is a sample footer template for documents." > /var/www/includes/footer.txt
RUN echo "Company contact information: support@docview.example.com" > /var/www/includes/contact.txt

ARG FLAG
RUN echo -n "${FLAG}" > /flag.txt
RUN chmod 644 /flag.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
