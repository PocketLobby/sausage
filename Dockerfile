FROM python:3.6

MAINTAINER @brycemcd <bryce@bridgetwonint.com>

RUN mkdir /opt/project

WORKDIR /opt/project

COPY requirements.txt /opt/project/requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "-u"]