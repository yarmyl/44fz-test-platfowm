FROM alpine:3.12.1
COPY requirements.txt /tmp/
ENV PIP_PROXY "http://tiger.bspb.ru:8080"
ENV HTTP_PROXY "http://tiger.bspb.ru:8080"
ENV HTTPS_PROXY "http://tiger.bspb.ru:8080"
RUN apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt
WORKDIR /opt/app/
EXPOSE 8080
COPY fz44-platform.py /opt/app/
CMD ["python3", "fz44-platform.py", "--web", "--url", "http://common-api-cft-etp:8080/cft-etp", "--delay", "5"]
