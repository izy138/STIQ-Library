FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend
EXPOSE 5002

CMD ["python", "app.py"]
