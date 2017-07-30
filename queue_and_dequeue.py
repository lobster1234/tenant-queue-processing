#!/usr/local/bin/python3
import boto3
import os
import sys
from datetime import datetime

print('The job is running for tenant', os.getenv('TENANT'))
start = datetime.now()
client = boto3.resource('sqs',region_name='us-east-1')
queue = client.create_queue(QueueName='batch_job_queue', Attributes={'DelaySeconds': '5'})
print('The Queue has been created as ', queue.url)
# In the real world, the queue will already have messages from an upstream process
# But in this case, let us populate it here
for i in range(1, 1000):
    queue.send_message(MessageBody=('This is message # ' + str(i)))
# Next, we dequeue these messages and print them out
while True:
    messages = queue.receive_messages(AttributeNames=['All'])
    if len(messages) > 0:
        for message in messages:
            print('Processing message -', message.body)
            message.delete()
    else:
        break
end = datetime.now()
print('The job has completed, all messages have been processed')
print('The job took', str((end - start).seconds), 'seconds')

