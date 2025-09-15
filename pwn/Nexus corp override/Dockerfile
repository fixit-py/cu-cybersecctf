FROM ubuntu:latest AS app

WORKDIR /app
COPY ./overflow1.c /app/overflow1.c
COPY ./overflow1 /app/overflow1
COPY ./flag.txt /app/flag.txt

FROM pwn.red/jail
COPY --from=app / /srv
RUN mkdir -p /srv/app
COPY --chmod=555 ./run /srv/app/run
ENV JAIL_PORT=10000 JAIL_PIDS=40 JAIL_MEM=10M JAIL_TIME=120
