FROM python:3.9

RUN mkdir "/server"

WORKDIR "/server"

COPY requirements.txt /server

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./

EXPOSE 60650

CMD ["python3", "/server/main.py"]