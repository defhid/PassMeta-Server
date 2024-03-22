FROM python:3.11

WORKDIR /configurator

RUN apt update
RUN apt install openssl -y

COPY modules /configurator/modules
COPY configurator.py /configurator/configurator.py

CMD python /configurator/configurator.py