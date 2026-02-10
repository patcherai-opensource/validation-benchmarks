FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ARG FLAG=""
ENV FLAG=${FLAG}

RUN echo '#!/bin/sh\nif [ -n "$FLAG" ]; then echo "$FLAG" > /flag.txt; fi\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

RUN if [ -n "$FLAG" ]; then echo "$FLAG" > /flag.txt; fi

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
