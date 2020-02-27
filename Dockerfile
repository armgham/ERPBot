FROM selenium/node-phantomjs:latest
USER root

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install build-essential libssl-dev libffi-dev python3-dev -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
<<<<<<< HEAD
=======

USER seluser

COPY ./ERPBot /app
ENTRYPOINT [ "python3" ]

CMD ["/app/app.py"] 
>>>>>>> 0232a8c8ba478511675f244aaa4e4b266fe3b608
