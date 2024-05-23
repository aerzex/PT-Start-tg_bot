FROM python:3.12

WORKDIR /app

COPY ./init.d/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY ./dockerbot.py /app

CMD ["python", "start.py"]
