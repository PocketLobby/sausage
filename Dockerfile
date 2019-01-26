# build with: docker build -t sausage .
# run with: docker run -it --rm --name sausage -v $(pwd):/opt/project sausage /bin/bash
FROM python:3.6

MAINTAINER @brycemcd <bryce@bridgetwonint.com>

RUN mkdir /opt/project
RUN mkdir /var/congress

WORKDIR /opt/project

RUN pip install --upgrade pip

COPY requirements.txt /opt/project/requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "-u"]