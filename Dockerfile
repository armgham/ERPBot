FROM selenium/node-phantomjs:latest
USER root

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install build-essential libssl-dev libffi-dev python3-dev -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
