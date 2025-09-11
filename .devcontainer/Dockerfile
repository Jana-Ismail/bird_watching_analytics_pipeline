FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

ENV DEBIAN_FRONTEND=noninteractive \
    AIRFLOW_HOME=/opt/airflow \
    PYTHONPATH="${PYTHONPATH}:/opt/airflow" 

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpq-dev \
    gcc \
    openssh-client \
    sudo \
    curl \
    sqlite3 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN groupadd --gid 50000 airflow && \
    useradd -m -s /bin/bash -u 50000 -g airflow airflow

RUN echo "airflow ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/airflow \
    && chmod 0440 /etc/sudoers.d/airflow

RUN mkdir -p ${AIRFLOW_HOME}/dags \
           ${AIRFLOW_HOME}/logs \
           ${AIRFLOW_HOME}/plugins \
           ${AIRFLOW_HOME}/config \
           ${AIRFLOW_HOME}/data && \
    chown -R airflow:airflow ${AIRFLOW_HOME} && \
    chmod -R 775 ${AIRFLOW_HOME}

USER airflow

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

WORKDIR ${AIRFLOW_HOME}
EXPOSE 8080



