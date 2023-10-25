FROM python:3.9

RUN mkdir /OverwatchQueueNotifier-server

WORKDIR /OverwatchQueueNotifier-server

COPY requirements.txt /OverwatchQueueNotifier-server/

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./

EXPOSE 60650

CMD ["python3", "main.py"]