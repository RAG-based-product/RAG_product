# Dockerfile
FROM --platform=linux/x86_64 python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    locales \
    redis-server \
    && sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen ru_RU.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /workspace

# Устанавливаем PYTHONPATH для корректного импорта модулей
ENV PYTHONPATH=/workspace

COPY requirements.txt /workspace/requirements.txt
# Копируем весь проект в образ
COPY . /workspace/

RUN pip install --no-cache-dir --upgrade -r /workspace/requirements.txt

# Создаем директории для логов supervisor
RUN mkdir -p /var/log/supervisor /var/run

# Копируем конфигурацию supervisor (только программы, без секции [supervisord])
COPY supervisord.conf /etc/supervisor/conf.d/services.conf

# Запускаем supervisor с основным конфигом (который автоматически включает файлы из conf.d/)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]

