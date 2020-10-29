FROM alpine:edge as build
RUN apk --update --no-cache add python3 py3-pip \
    perl perl-json \
    alpine-sdk mariadb-connector-c-dev mariadb-connector-c \
    openssl
RUN apk --update --no-cache add python3-dev
RUN pip3 install mariadb bottle gunicorn

FROM alpine:edge
RUN apk --update --no-cache add python3 \
    perl perl-json \
    mariadb-connector-c \
    openssl

COPY --from=build /usr/lib/python3.8/site-packages/ /usr/lib/python3.8/site-packages/
COPY --from=build /usr/bin/gunicorn /usr/bin/gunicorn

COPY lynis-report-converter.pl /opt/
COPY main.py /opt/
COPY prod.sh /opt/
WORKDIR /opt/
USER nobody
