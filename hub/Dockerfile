FROM python:3.7-stretch

COPY requirements.txt /src/
RUN pip install -r /src/requirements.txt

COPY . /src/
RUN pip install /src && overwatch-hub --version
# ^^^ Run with --version just to check that it can be executed

EXPOSE 8080

CMD ["overwatch-hub", "--conf", "/conf/overwatch_hub.yaml"]
