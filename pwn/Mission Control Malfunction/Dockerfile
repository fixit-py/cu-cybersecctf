FROM ubuntu:latest AS app
WORKDIR /app/
COPY ./handoff /app/handoff

FROM pwn.red/jail
COPY --from=app / /srv
RUN mkdir -p /srv/app
COPY --chmod=555 ./run /srv/app/run

ENV JAIL_PORT=15000 JAIL_PIDS=40 JAIL_MEM=10M JAIL_TIME=120
