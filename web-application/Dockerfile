FROM python:3.13-slim

# Установим pip и зависимости
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Переключаемся в папку с backend
WORKDIR /app/backend

EXPOSE 8000

# Запускаем FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
