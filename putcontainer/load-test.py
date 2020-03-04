import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import dns.resolver
import os 
import pprint 
import curses
import json

def get_queuename():
    bytes_response = dns.resolver.query("filesqueue.loadtest","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("filesqueue.loadtest={0}".format(response))
    print(response)
    return response

def get_bucketname():
    bytes_response = dns.resolver.query("bucket.loadtest","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("bucket.loadtest={0}".format(response))
    return response

def upload_to_bucket(local_file, bucket, s3_file):
    s3 = boto3.client('s3')

    try:
        s3_response = s3.upload_file(local_file, bucket, s3_file)
        # unique_upload_id = s3_response.?
        print("Upload Successful")
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
    print(response['MessageId'])



def start_uploads(bucketname, queueURL, sqs_client):
    var=0
    # while var < 100:
    for var in range(100):
    # while True:
        now = datetime.now() # current date and time
        print(now)
        # s3_file_name="diagram_" + now.strftime("%H:%M:%S:%f") + ".png"
        s3_file_name=now.strftime("%f_%H:%M:%S:%f") + "_diagram" + ".png"
        print(s3_file_name)
        # uploaded = upload_to_bucket('/home/ec2-user/environment/Amazon-S3-Bucket-Load-Test/container/diagram.png', 'amazon-s3-bucket-load-test-storagebucket-knlgpd3wpz0n', s3_file_name)
        # done = datetime.now()
        uploaded = upload_to_bucket('/app/diagram.png', bucketname, s3_file_name)
        if uploaded:
            enqueue_object(bucketname, s3_file_name, queueURL, sqs_client)
        else:
            print("Error uploading object: {0} to bucket: {1}".format(s3_file_name, bucketname))




if __name__ == '__main__':
    # Get the list of user's 
    # environment variables 
    env_var = os.environ 
    # Print the list of user's 
    # environment variables 
    print("User's Environment variables:") 
    pprint.pprint(dict(env_var), width = 1) 

    QUEUEURL = get_queuename()
    BUCKETNAME = get_bucketname()
    

    sqs_client = boto3.client('sqs')
    start_uploads(BUCKETNAME, QUEUEURL, sqs_client)













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



