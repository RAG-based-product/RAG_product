FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    locales \
    curl \
    && sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen ru_RU.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
ENV PYTHONPATH=/workspace

# Копируем requirements из backend
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /workspace/requirements.txt

# Копируем backend директорию в workspace
COPY . /workspace/

CMD ["/bin/bash"]