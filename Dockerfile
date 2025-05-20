FROM apache/airflow:2.11.0
USER root
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
USER airflow
ADD requirements.txt .
RUN pip install -r requirements.txt
