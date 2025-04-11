FROM python:3.12-slim

WORKDIR /api
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000


CMD ["fastapi", "run", "main.py"]