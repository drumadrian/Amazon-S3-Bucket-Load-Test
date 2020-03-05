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

patch_all()


def get_queueURL():
    bytes_response = dns.resolver.query("filesqueue.loadtest","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("filesqueue.loadtest={0}".format(response))
    print(response)
    return response


def dequeue_message(QUEUEURL, sqs_client):
    ###### Example of string data that was sent:#########
    # payload = { 
    # "bucketname": bucketname, 
    # "s3_file_name": s3_file_name
    # }
    ################################################

    receive_message_response = sqs_client.receive_message(
        QueueUrl=QUEUEURL,
        # AttributeNames=[
        #     'All'|'Policy'|'VisibilityTimeout'|'MaximumMessageSize'|'MessageRetentionPeriod'|'ApproximateNumberOfMessages'|'ApproximateNumberOfMessagesNotVisible'|'CreatedTimestamp'|'LastModifiedTimestamp'|'QueueArn'|'ApproximateNumberOfMessagesDelayed'|'DelaySeconds'|'ReceiveMessageWaitTimeSeconds'|'RedrivePolicy'|'FifoQueue'|'ContentBasedDeduplication'|'KmsMasterKeyId'|'KmsDataKeyReusePeriodSeconds',
        # ],
        # MessageAttributeNames=[
        #     'string',
        # ],
        MaxNumberOfMessages=1
        # VisibilityTimeout=123,
        # WaitTimeSeconds=123,
        # ReceiveRequestAttemptId='string'
    )

    if 'Messages' in receive_message_response:
        number_of_messages = len(receive_message_response['Messages'])
        print("\n received {0} messages!! ....Processing message \n".format(number_of_messages))
    else:
        print("\n received 0 messages!! waiting.....5 seconds before retrying \n")
        time.sleep(5)
        return ["wait", "wait"]

    message_body=json.loads(receive_message_response['Messages'][0]['Body'])
    print("message_body = {0} \n".format(message_body))
    bucketname = message_body['bucketname']
    objectkey = message_body['s3_file_name']

    ReceiptHandle = receive_message_response['Messages'][0]['ReceiptHandle']
    delete_message_response = sqs_client.delete_message(
    QueueUrl=QUEUEURL,
    ReceiptHandle=ReceiptHandle
    )
    print("delete_message_response = {0}".format(delete_message_response))

    return [bucketname, objectkey]





def start_downloads(QUEUEURL, sqs_client, s3_client):
    # for var in range(100):
    while True:
        now = datetime.now() # current date and time
        print("now={0}".format(now))

        message = dequeue_message(QUEUEURL, sqs_client)
        print("message={0}".format(message))
        bucketname = message[0]
        objectkey = message[1]
        if bucketname != "wait":
            try:
                get_object_response = s3_client.get_object(
                    Bucket=bucketname,
                    # IfMatch='string',
                    # IfModifiedSince=datetime(2015, 1, 1),
                    # IfNoneMatch='string',
                    # IfUnmodifiedSince=datetime(2015, 1, 1),
                    Key=objectkey
                    # Range='string',
                    # ResponseCacheControl='string',
                    # ResponseContentDisposition='string',
                    # ResponseContentEncoding='string',
                    # ResponseContentLanguage='string',
                    # ResponseContentType='string',
                    # ResponseExpires=datetime(2015, 1, 1),
                    # VersionId='string',
                    # SSECustomerAlgorithm='string',
                    # SSECustomerKey='string',
                    # RequestPayer='requester',
                    # PartNumber=123
                )
            except ClientError as e:
                print("Error downloading object: {0} from bucket: {1}".format(objectkey, bucketname))



if __name__ == '__main__':
    # Get the list of user's 
    # environment variables 
    env_var = os.environ 
    # Print the list of user's 
    # environment variables 
    print("User's Environment variable:") 
    pprint.pprint(dict(env_var), width = 1) 

    QUEUEURL = get_queueURL()
    
    sqs_client = boto3.client('sqs')
    s3_client = boto3.client('s3')

    start_downloads(QUEUEURL, sqs_client, s3_client)








