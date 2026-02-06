FROM python:3.13-alpine

RUN apk add --no-cache iw

WORKDIR /app
COPY iwscan.py .

ENV INTERFACE=wlan0
ENV PORT=5024

EXPOSE $PORT

CMD python iwscan.py -i $INTERFACE -p $PORT