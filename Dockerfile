FROM alpine:3.12.1
COPY requirements.txt /tmp/
RUN export PIP_PROXY="http://tiger.bspb.ru:8080" && \
    export HTTP_PROXY="http://tiger.bspb.ru:8080" && \
    export HTTPS_PROXY="http://tiger.bspb.ru:8080"
RUN apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt
WORKDIR /opt/app/
EXPOSE 8080
COPY fz44-platform.py /opt/app/
CMD python3 fz44-platform.py --web --url $FZ44_URL --delay $FZ44_DELAY --debug $FZ44_DEBUG
