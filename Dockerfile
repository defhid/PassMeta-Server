FROM python:3.11

WORKDIR /deploy

COPY requirements.txt /deploy/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /deploy/requirements.txt

COPY App /deploy/App
COPY main.py /deploy/main.py

CMD python /deploy/main.py