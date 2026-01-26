FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as root? Ideally not, but simpler for PVC permissions in MVP
# In production, use fsGroup in StatefulSet
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
