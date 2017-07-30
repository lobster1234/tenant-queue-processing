This is a Dockerfile for a task defintion for AWS batch.

The python script simply queues 1000 messages, and dequeues them to define a task. It also prints out an environment variable, that can be used to make decisions or pull configuration, etc. in real world use cases.

Here are the steps to use this repo. Please note that I am using `us-east-1`. **Do not copy paste these steps without knowing what region you want to use.**

> You can modify the number of messages if 1000 is too much. I wanted the batch job to run for a while to be able to see the state transition.

0. Make sure you have `boto3` and `python3` installed locally. Also, your AWS CLI is configured with credentials that have Full SQS access. Also, you should have `docker` installed.

1. Test the python script locally

``` 
bash-3.2$ export TENANT=foo
bash-3.2$ python3 queue_and_dequeue.py
The job is running for tenant foo
The Queue has been created as  https://queue.amazonaws.com/**************/batch_job_queue
Processing message - This is message # 2
Processing message - This is message # 1
Processing message - This is message # 7
Processing message - This is message # 3
...
The job has completed, all messages have been processed
The job took 308 seconds
```
2. Create an image - your output will vary, as this is after many runs, so not as much going on.
```
bash-3.2$ docker build .
Sending build context to Docker daemon  61.95kB
Step 1/6 : FROM ubuntu:latest
 ---> 14f60031763d
Step 2/6 : RUN apt-get -y update && apt-get -y upgrade
 ---> Using cache
 ---> c88baea8cbf0
Step 3/6 : RUN apt-get install -y python3-pip
 ---> Using cache
 ---> 7819a041209c
Step 4/6 : RUN pip3 install boto3
 ---> Using cache
 ---> 9a9e9d0dc34f
Step 5/6 : COPY queue_and_dequeue.py /tmp
 ---> Using cache
 ---> 4aee548d86d2
Step 6/6 : CMD python3 /tmp/queue_and_dequeue.py
 ---> Using cache
 ---> 5f26e169331d
Successfully built 5f26e169331d
```
3. Tag this image - **use the image ID you got from the previous command.**
```
bash-3.2$ docker tag 5f26e169331d tenant-queue-processing:latest
```
4. Try to run the container
```
bash-3.2$ docker run tenant-queue-processing:latest
The job is running for tenant None
Traceback (most recent call last):
  File "/tmp/queue_and_dequeue.py", line 10, in <module>
  ....
  File "/usr/local/lib/python3.5/dist-packages/botocore/auth.py", line 340, in add_auth
    raise NoCredentialsError
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```
Do not worry about this error - since the container does not have access to the credentials, it fails. When run via ECS, the ECS role will have access to SQS, so it will run just fine.

5. Create a repo in AWS ECS 

 Go to https://console.aws.amazon.com/ecs/home?region=us-east-1#/repositories/create/new and use the name `tenent-queue-processing` and click 'Next Step'
 Keep the next page open, as it will help you push the we just created to ECR. The below steps map to the steps suggested in that page.
 
6. Login to AWS ECS Registry
```
bash-3.2$ aws ecr get-login --no-include-email --region us-east-1
docker login -u AWS -p *******
```
Copy paste the `docker login ....` output and hit enter. These are the credentials to ECR, Amazon's version of Dockerhub.

```
bash-3.2$ docker login -u AWS -p *******
Login Succeeded
```
7. Tag the image for ECS
```
bash-3.2$ docker tag tenant-queue-processing:latest *************.dkr.ecr.us-east-1.amazonaws.com/tenant-queue-processing:latest
```

8. Push the image to ECR
```
bash-3.2$ docker push *************.dkr.ecr.us-east-1.amazonaws.com/tenant-queue-processing:latest
The push refers to a repository [*************..dkr.ecr.us-east-1.amazonaws.com/tenant-queue-processing]
...
...
latest: digest: sha256:*********7e8f5a8b585382e10fa7a44a19d4a8ef1ddf3ba89618fd6ecf1b58b size: 2200
```
9. Now you're all set to launch this as AWS Batch Job. Use the ECR Repository URI as the "image" option when creating a job definition.




