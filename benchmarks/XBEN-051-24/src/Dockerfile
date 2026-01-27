FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
ENV FLAG=${FLAG:-@FLAG@}

# Create a startup script to handle dynamic flag substitution
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "$FLAG" ] && [ "$FLAG" != "@FLAG@" ]; then' >> /entrypoint.sh && \
    echo '    sed -i "s/@FLAG@/$FLAG/g" /app/secret.txt' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
