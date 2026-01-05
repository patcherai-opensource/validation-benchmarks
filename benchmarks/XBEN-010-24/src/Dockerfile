
FROM python:3.9-slim


RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null
ENV BASE_URL=http://localhost:5000

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ARG FLAG
ENV FLAG_VALUE=${FLAG}

# Create a script to substitute flag at runtime
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "$FLAG" ]; then' >> /entrypoint.sh && \
    echo '  sed -i "s/@FLAG@/$FLAG/g" secret.txt' >> /entrypoint.sh && \
    echo 'elif [ -n "$FLAG_VALUE" ]; then' >> /entrypoint.sh && \
    echo '  sed -i "s/@FLAG@/$FLAG_VALUE/g" secret.txt' >> /entrypoint.sh && \
    echo 'else' >> /entrypoint.sh && \
    echo '  echo "Warning: No FLAG provided, using placeholder"' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
