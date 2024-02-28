FROM python:3.11.6-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV FLASK_APP=app.py

VOLUME /app/instance

EXPOSE 5000
CMD flask run --host=0.0.0.0 --port=5000
