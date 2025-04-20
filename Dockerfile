FROM python:3.9-slim

WORKDIR /app

COPY web-application/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data

COPY web-application/ .

EXPOSE 8000

CMD ["python", "app.py"]