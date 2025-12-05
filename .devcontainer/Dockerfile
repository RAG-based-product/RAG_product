# Dockerfile
FROM --platform=linux/x86_64 python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y locales && \
    sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen ru_RU.UTF-8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /workspace

# Устанавливаем PYTHONPATH для корректного импорта модулей
ENV PYTHONPATH=/workspace

COPY requirements.txt /workspace/requirements.txt
# Копируем весь проект в образ
COPY . /workspace/

RUN pip install --no-cache-dir --upgrade -r /workspace/requirements.txt

# Запускаем приложение
CMD ["python3", "-m", "main"]

