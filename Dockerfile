FROM alpine:3.12

WORKDIR /stormberry/src
COPY src/ .
WORKDIR /stormberry
COPY setup.py .
COPY config.ini.example .
COPY README.md .
RUN apk add --no-cache python3
RUN apk add --no-cache py3-pip
RUN pip3 install --no-cache --upgrade pip setuptools
Run pip3 install -U Flask
RUN python3 setup.py install
CMD ["stormberry-demo-server"]
