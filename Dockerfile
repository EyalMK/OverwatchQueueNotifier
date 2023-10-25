FROM python:3.9
LABEL authors="Eyal Maklada"

RUN mkdir /OverwatchQueueNotifier-server

WORKDIR /OverwatchQueueNotifier-server

COPY requirements.txt /OverwatchQueueNotifier-server/

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./OverwatchQueueNotifier-server

EXPOSE 60650

CMD ["python3", "main.py"]