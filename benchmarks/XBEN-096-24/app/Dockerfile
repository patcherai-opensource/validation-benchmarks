FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Plant the flag at build time
ARG FLAG=""
RUN echo "${FLAG}" > /flag.txt && chmod 444 /flag.txt

EXPOSE 5000

# Use entrypoint to handle runtime flag injection if needed
RUN printf '#!/bin/sh\n\
if [ -n "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then\n\
  echo "$FLAG" > /flag.txt\n\
fi\n\
unset FLAG\n\
exec "$@"\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]

