# Dockerfile
FROM --platform=linux/x86_64 python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y locales && \
    sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen ru_RU.UTF-8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /workspace/requirements.txt

