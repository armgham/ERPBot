FROM centos:centos7

RUN yum update -y

RUN yum install -y glibc fontconfig freetype freetype-devel fontconfig-devel wget bzip2 mysql-devel gcc

RUN yum -y install python3 python3-devel

RUN yum clean all

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share/
RUN ln -sf /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin



COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY . /
ENTRYPOINT [ "python3" ]

#COPY x.py /app2.py

CMD ["/app.py"] 
