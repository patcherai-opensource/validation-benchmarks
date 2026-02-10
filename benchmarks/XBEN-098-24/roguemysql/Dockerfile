FROM python:3.9-slim

WORKDIR /app

COPY rogue_mysql.py /app/

EXPOSE 3306 8080

CMD ["python3", "-u", "rogue_mysql.py"]
