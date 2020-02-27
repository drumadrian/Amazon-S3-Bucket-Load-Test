import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import dns.resolver
import os 
import pprint 




# Get the list of user's 
# environment variables 
env_var = os.environ 
  
# Print the list of user's 
# environment variables 
print("User's Environment variable:") 
pprint.pprint(dict(env_var), width = 1) 








def get_bucketname(bucket_name, object_name):
    response = dns.resolver.query("bucket.loadtest","TXT").response.answer[0][-1].strings[0]
    print(response)
    return response

def get_queuename(bucket_name, object_name):
    response = dns.resolver.query("filesqueue.loadtest","TXT").response.answer[0][-1].strings[0]
    print(response)
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



def enqueue_object(bucketname, s3_file_name, queuename, sqs_client):
    payload = { 
    "bucketname": bucketname, 
    "s3_file_name": s3_file_name
    }
    
    queue_url = 'SQS_QUEUE_URL'

    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            'Title': {
                'DataType': 'String',
                'StringValue': 'The Whistler'
            },
            'Author': {
                'DataType': 'String',
                'StringValue': 'John Grisham'
            },
            'WeeksOn': {
                'DataType': 'Number',
                'StringValue': '6'
            }
        },
        MessageBody=(
            'Information about current NY Times fiction bestseller for '
            'week of 12/11/2016.'
        )
    )

print(response['MessageId'])


    response = sqs_client.send_message(
        QueueUrl = 'string',
        MessageBody = payload,
        DelaySeconds = 1,
        MessageAttributes = {
            'string': {
                'StringValue': 'string',
                'StringValue': 'string',
                'DataType': 'string'
            }
        },
        MessageSystemAttributes = {
            'string': {
                'StringValue': 'string',
                'BinaryValue': b'bytes',
                'StringListValues': [
                    'string',
                ],
                'BinaryListValues': [
                    b'bytes',
                ],
                'DataType': 'string'
            }
        },
        MessageDeduplicationId = 'string',
        MessageGroupId = 'string'
    )





def start_uploads(bucketname, queuename, sqs_client):
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
            enqueue_object(bucketname, s3_file_name, queuename, sqs_client)

        

if __name__ == '__main__':
    sqs_client = boto3.client('sqs')
    bucketname = get_bucketname()
    queuename = get_queuename()
    start_uploads(bucketname, queuename, sqs_client)













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



