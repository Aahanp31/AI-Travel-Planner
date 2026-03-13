FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 4000
CMD ["gunicorn", "--bind", "0.0.0.0:4000", "--timeout", "180", "--workers", "4", "--worker-class", "gthread", "--threads", "2", "app:app"]
