FROM python:3.9-slim

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install fastapi uvicorn python-multipart jinja2

# Create app directory
WORKDIR /app

# Copy application files
COPY main.py /app/
COPY templates /app/templates/

# Create models directory structure with sample models
RUN mkdir -p /app/models/transfo-xl-wt103 && \
    mkdir -p /app/models/gpt2-small && \
    mkdir -p /app/models/bert-base-uncased

# Create sample vocab.pkl files for the pretrained models (legitimate pickle files)
RUN python3 -c "import pickle; vocab = {'<unk>': 0, '<eos>': 1, 'the': 2, 'a': 3}; \
    pickle.dump(vocab, open('/app/models/transfo-xl-wt103/vocab.pkl', 'wb'))"
RUN python3 -c "import pickle; vocab = {'<|endoftext|>': 0, 'the': 1, 'and': 2}; \
    pickle.dump(vocab, open('/app/models/gpt2-small/vocab.pkl', 'wb'))"
RUN python3 -c "import pickle; vocab = {'[PAD]': 0, '[UNK]': 1, '[CLS]': 2, '[SEP]': 3}; \
    pickle.dump(vocab, open('/app/models/bert-base-uncased/vocab.pkl', 'wb'))"

# Accept FLAG as build argument and store it securely
ARG FLAG
RUN echo "${FLAG}" > /root/flag.txt && chmod 600 /root/flag.txt

# Create a non-root user for the application but it still needs to read pickle files
# The flag is in /root which is only readable by root, but the process runs as root
# for the pickle exploit to be able to read the flag
EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
