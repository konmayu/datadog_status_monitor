FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY datadog_status_monitor.py .

CMD ["python", "datadog_status_monitor.py"]
