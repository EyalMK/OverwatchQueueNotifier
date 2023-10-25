FROM python:3.9

RUN mkdir /home/OverwatchQueueNotifier/server

WORKDIR /home/OverwatchQueueNotifier/server

COPY requirements.txt /home/OverwatchQueueNotifier/server

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./

EXPOSE 60650

CMD ["python", "/server/main.py"]