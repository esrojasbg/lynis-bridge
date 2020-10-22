FROM alpine:edge
RUN apk --update --no-cache add python3 py3-pip perl perl-json alpine-sdk mariadb-connector-c-dev mariadb-connector-c
RUN apk --update --no-cache add python3-dev
RUN pip3 install mariadb bottle

COPY lynis-report-converter.pl /opt/
COPY main.py /opt/
WORKDIR /opt/
CMD python3 main.py