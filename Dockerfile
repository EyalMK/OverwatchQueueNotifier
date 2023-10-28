FROM python:3.9

WORKDIR /app

COPY /server /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 60650

CMD ["python3", "/app/main.py"]