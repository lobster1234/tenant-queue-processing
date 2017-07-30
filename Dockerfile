FROM ubuntu:latest
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y python3-pip
RUN pip3 install boto3
COPY queue_and_dequeue.py /tmp 
CMD python3 /tmp/queue_and_dequeue.py
