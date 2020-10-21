FROM alpine:3.12
RUN apk add --update --no-cache python3 perl perl-json py3-bottle

COPY lynis-report-converter.pl /opt/
COPY main.py /opt/
WORKDIR /opt/
CMD python3 main.py