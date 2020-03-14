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

OBJECTS_PER_CONTAINER = "∞"

def get_queuename():
    bytes_response = dns.resolver.query("filesqueue.loadtest.com","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("\n filesqueue.loadtest.com= {0}\n".format(response))
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
    var=0
    # for var in range(OBJECTS_PER_CONTAINER):
    while True:

        now = datetime.now() # current date and time
        time_now = now.strftime("%H:%M:%S.%f")
        print("\n In start_downloads() Time now: " + time_now)

        # Start a subsegment for dequeue_message()
        subsegment = xray_recorder.begin_subsegment('function: dequeue_message')
        message = dequeue_message(QUEUEURL, sqs_client)
        xray_recorder.put_metadata("message from dequeue_message()", message)
        print("\n message={0}\n".format(message))
        # Close the subsegment
        xray_recorder.end_subsegment()

        # Start a subsegment for get_object()
        subsegment = xray_recorder.begin_subsegment('function: get_object')
        bucketname = message[0]
        objectkey = message[1]

        now = datetime.now() # current date and time
        time_now = now.strftime("%H:%M:%S.%f")
        xray_recorder.put_annotation("Version", "1.0")
        xray_recorder.put_annotation("Developer", "Adrian")
        xray_recorder.put_metadata("function", __name__)
        xray_recorder.put_metadata("objects per container", OBJECTS_PER_CONTAINER)
        xray_recorder.put_metadata("system time H:M:S.milliseconds", time_now)
        document = xray_recorder.current_segment()
        document.set_user("S3 GET User")

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

        # Close the subsegment
        xray_recorder.end_subsegment()
        # Set the user back to: GET Container User
        document = xray_recorder.current_segment()
        document.set_user("GET Container User")


if __name__ == '__main__':

    # Start a segment
    segment = xray_recorder.begin_segment('function: __main__')
    now = datetime.now() # current date and time
    time_now = now.strftime("%H:%M:%S.%f")
    xray_recorder.put_annotation("Version", "4.0")
    xray_recorder.put_annotation("Developer", "Adrian")
    xray_recorder.put_metadata("function", __name__)
    xray_recorder.put_metadata("objects per container", OBJECTS_PER_CONTAINER)
    xray_recorder.put_metadata("system time H:M:S.milliseconds", time_now)
    document = xray_recorder.current_segment()
    document.set_user("GET Container User")

    # Get and Print the list of user's environment variables 
    env_var = os.environ 
    print("\n User's Environment variables:") 
    pprint.pprint(dict(env_var), width = 1) 

    # Start a subsegment for function: get_queuename 
    subsegment = xray_recorder.begin_subsegment('function: get_queuename')
    subsegment.put_annotation("Subsegment_Developer", "Adrian")
    QUEUEURL = get_queuename()
    # QUEUEURL = "https://sqs.us-west-2.amazonaws.com/696965430582/Amazon-S3-Bucket-Load-Test-EcsTaskSqsQueue-1HTOHJVBT359V"
    subsegment.put_metadata("QUEUEURL", QUEUEURL)
    xray_recorder.end_subsegment()
    
    sqs_client = boto3.client('sqs')
    s3_client = boto3.client('s3')

    start_downloads(QUEUEURL, sqs_client, s3_client)

    # Close the segment
    xray_recorder.end_segment()































