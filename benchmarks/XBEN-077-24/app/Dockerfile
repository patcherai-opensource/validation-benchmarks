FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN pip3 install lxml==5.2.2 itsdangerous==2.1.2

COPY . /app

# Create template upload directory
RUN mkdir -p /app/var/invoices/templates

# Create entrypoint for flag injection
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Remove files not needed in production
RUN rm -f /app/flag.txt

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
