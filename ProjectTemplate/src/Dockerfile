FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . .

#   (5000 ll server , 8501 ll front )ports 
EXPOSE 5000 8501
