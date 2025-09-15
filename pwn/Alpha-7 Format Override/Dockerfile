FROM ubuntu:latest AS app
WORKDIR /app/
COPY ./format1.c /app/format1.c
COPY ./format1 /app/format1
COPY ./flag.txt /app/flag.txt

FROM pwn.red/jail
COPY --from=app / /srv
RUN mkdir -p /srv/app
COPY --chmod=555 ./run /srv/app/run

ENV JAIL_PORT=9000 JAIL_PIDS=40 JAIL_MEM=10M JAIL_TIME=120
