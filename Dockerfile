FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/docs && \
    mkdir -p /app/app && \
    echo '{"default_language": "Japanese", "theme": "light", "api_key": ""}' > /app/app/config.json

COPY . .

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
