FROM python:3.9-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
ENV FLAG=${FLAG}

RUN sed -i s/@FLAG@/$FLAG/g secret.txt

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
