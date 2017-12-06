# This file has been modified from the original

FROM node:6

RUN mkdir -p /tmp/service && \
    mkdir -p /app

ADD ./mock-cds-backend/package.json /tmp/service/

RUN cd /tmp/service && npm install

ADD . /app
WORKDIR /app

RUN mv run-backend /bin && \
    mv /tmp/service/node_modules /app/mock-cds-backend

ENV HTTP_PORT_BACKEND 8099

CMD run-backend
