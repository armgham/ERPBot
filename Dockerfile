FROM python:3.8.2-buster

RUN apt-get update
#RUN apt-get phantomjs
RUN apt-get install build-essential chrpath libssl-dev libxft-dev libfreetype6-dev libfreetype6 libfontconfig1-dev libfontconfig1 wget libffi-dev -y
#RUN apt-get install libffi-dev python3-dev wget -y
#RUN apt-get install python3 -y
#RUN apt-get install python3-pip -y


RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share/
RUN ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/

RUN touch openssl.cnf
#RUN export OPENSSL_CONF=$WORKSPACE/openssl.cnf

ENV OPENSSL_CONF=/openssl.cnf

COPY ./requirements.txt /tmp/
#RUN pip install pip --upgrade
RUN pip install -r /tmp/requirements.txt

# USER seluser

COPY ./ERPBot /app
ENTRYPOINT [ "python" ]

COPY x.py /app/app2.py

CMD ["/app/app2.py"] 
