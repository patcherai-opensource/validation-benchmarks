FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY website /app/

# Create a startup script to handle runtime flag injection
# The flag is written to /flag.html - the path traversal vulnerability requires files with extensions
# Since the vulnerable endpoint appends .html to paths without extensions, the flag must have .html extension
# or be accessed with full extension: /page?layout=../../../flag.html
RUN echo '#!/bin/bash\necho -n "${FLAG:-PLACEHOLDER_FLAG}" > /flag.html\nexec flask run --host=0.0.0.0 -p 80' > /start.sh && chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
