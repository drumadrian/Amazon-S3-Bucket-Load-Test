import boto3
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import ClientError
from datetime import datetime
import dns.resolver
import os 
import pprint
import json 
import time

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

xray_recorder.configure(
    # service='PUT - S3 Bucket Load Test Container',
    # sampling=False,
    # context_missing='LOG_ERROR'
    # plugins=('ECSPlugin')
    # daemon_address='127.0.0.1:3000',
    # dynamic_naming='*put.loadtest*'
)


# xray_recorder.configure(service='PUT - S3 Bucket Load Test Container')
# plugins = ('ECSPlugin','ElasticBeanstalkPlugin', 'EC2Plugin')
# xray_recorder.configure(plugins=plugins)

# patch_all()
# https://docs.aws.amazon.com/xray/latest/devguide/xray-guide.pdf


def get_queuename():
    bytes_response = dns.resolver.query("filesqueue.loadtest.com","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("\n filesqueue.loadtest.com= {0}\n".format(response))
    print(response)
    return response

def get_bucketname():
    bytes_response = dns.resolver.query("bucket.loadtest.com","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("\n bucket.loadtest.com= {0}\n".format(response))
    return response

def upload_to_bucket(local_file, bucket, s3_file):
    s3 = boto3.client('s3')

    try:
        s3_response = s3.upload_file(local_file, bucket, s3_file)
        # unique_upload_id = s3_response.?
        print("S3 Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False



def enqueue_object(bucketname, s3_file_name, queueURL, sqs_client):
    payload = { 
    "bucketname": bucketname, 
    "s3_file_name": s3_file_name
    }
    str_payload = json.dumps(payload)
    
    response = sqs_client.send_message(
        QueueUrl=queueURL,
        DelaySeconds=1,
        # MessageAttributes=,
        MessageBody=str_payload        
        # MessageBody=(
        #     'Information about current NY Times fiction bestseller for '
        #     'week of 12/11/2016.'
        # )
    )
    print("send_message() to SQS Successful\n\n")
    # print(response['MessageId'])



def start_uploads(bucketname, queueURL, sqs_client):
    var=0
    # while var < 100:
    for var in range(10):
    # while True:

        now = datetime.now() # current date and time
        print("\n Time now: " + now.strftime("%H:%M:%S.%f"))

        # s3_file_name="diagram_" + now.strftime("%H:%M:%S.%f") + ".png"
        s3_file_name=now.strftime("%f_%H:%M:%S.%f") + "_diagram" + ".png"
        print("\n s3_file_name: {0}\n".format(s3_file_name))

        # Start a subsegment for upload_to_bucket()
        subsegment = xray_recorder.begin_subsegment('function: upload_to_bucket')
        # uploaded = upload_to_bucket('/app/diagram.png', bucketname, s3_file_name)
        uploaded = upload_to_bucket('diagram.png', bucketname, s3_file_name)
        # Close the subsegment
        xray_recorder.end_subsegment()

        # Start a subsegment for enqueue_object()
        subsegment = xray_recorder.begin_subsegment('function: enqueue_object')
        if uploaded:
            enqueue_object(bucketname, s3_file_name, queueURL, sqs_client)
        else:
            print("Error uploading object: {0} to bucket: {1}".format(s3_file_name, bucketname))
        # Close the subsegment and segment
        xray_recorder.end_subsegment()



if __name__ == '__main__':
    
    now = datetime.now() # current date and time
    time_now = now.strftime("%H:%M:%S.%f")

    # Start a segment
    segment = xray_recorder.begin_segment('function: __main__')
    # xray_recorder.put_annotation("annotation1", "10");
    # xray_recorder.put_metadata("metadata1", "PUTmetadata");
    xray_recorder.put_annotation("Version", "4.0");
    xray_recorder.put_annotation("Developer", "Adrian");
    xray_recorder.put_metadata("function", __name__);
    xray_recorder.put_metadata("objects per container", 10);
    xray_recorder.put_metadata("system time H:M:S.milliseconds", time_now);
    document = xray_recorder.current_segment()
    document.set_user("PUT Container User");

    # Get and Print the list of user's environment variables 
    env_var = os.environ 
    print("\n User's Environment variables:") 
    pprint.pprint(dict(env_var), width = 1) 

    # Start a subsegment for function: get_queuename 
    subsegment = xray_recorder.begin_subsegment('function: get_queuename')
    subsegment.put_annotation("Subsegment_Developer", "Adrian");
    # QUEUEURL = get_queuename()
    QUEUEURL = "https://sqs.us-west-2.amazonaws.com/696965430582/Amazon-S3-Bucket-Load-Test-EcsTaskSqsQueue-1HTOHJVBT359V"
    subsegment.put_metadata("QUEUEURL", QUEUEURL);
    xray_recorder.end_subsegment()

    # Start a subsegment for function: get_bucketname 
    subsegment = xray_recorder.begin_subsegment('function: get_bucketname')
    subsegment.put_annotation("Subsegment_Developer", "Adrian");
    # BUCKETNAME = get_bucketname()
    BUCKETNAME = "amazon-s3-bucket-load-test-storagebucket-18u2ld8f2gi2i"
    subsegment.put_metadata("BUCKETNAME", BUCKETNAME);
    xray_recorder.end_subsegment()
    
    sqs_client = boto3.client('sqs')
    start_uploads(BUCKETNAME, QUEUEURL, sqs_client)

    # Close the segment
    xray_recorder.end_segment()










# SCRATCH
# year = now.strftime("%Y")
# print("year:", year)

# month = now.strftime("%m")
# print("month:", month)

# day = now.strftime("%d")
# print("day:", day)

# time = now.strftime("%H:%M:%S")
# print("time:", time)

# date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
# print("date and time:",date_time) 



