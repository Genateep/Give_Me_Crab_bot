FROM python:3
ENV PYTHONUNBUFFERED 1
ADD . /apps/crab
WORKDIR /apps/crab
COPY docker/src/backend/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt