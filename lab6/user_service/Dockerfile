FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install python-multipart

COPY . .

CMD ["bash", "-c", "python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
