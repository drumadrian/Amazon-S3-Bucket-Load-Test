import boto3
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import ClientError
from datetime import datetime
import dns.resolver
import os 
import pprint
import json 
import time

import oneagent # SDK initialization functions
import oneagent.sdk as onesdk # All other SDK functions.
from oneagent.common import MessagingDestinationType
from oneagent.common import AgentState


################################################################################################################
#   Get the queue name to dequeue messages 
################################################################################################################
def get_queuename():
    bytes_response = dns.resolver.query("filesqueue.loadtest.com","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("\n filesqueue.loadtest.com= {0}\n".format(response))
    print(response)
    return response


################################################################################################################
#   Get messages from queue 
################################################################################################################
def dequeue_message(QUEUEURL, sqs_client):
    ###### Example of string data that was sent:#########
    # payload = { 
    # "bucketname": bucketname, 
    # "s3_file_name": s3_file_name
    # }
    ################################################

    receive_message_response = sqs_client.receive_message(
        QueueUrl=QUEUEURL,
        MaxNumberOfMessages=1
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
    while True:

        now = datetime.now() # current date and time
        time_now = now.strftime("%H:%M:%S.%f")
        print("\n In start_downloads() Time now: " + time_now)

        message = dequeue_message(QUEUEURL, sqs_client)
        print("\n message={0}\n".format(message))

        bucketname = message[0]
        objectkey = message[1]

        now = datetime.now() # current date and time
        time_now = now.strftime("%H:%M:%S.%f")

        if bucketname != "wait":
            try:
                get_object_response = s3_client.get_object(
                    Bucket=bucketname,
                    Key=objectkey
                )
            except ClientError as e:
                print("Error downloading object: {0} from bucket: {1}".format(objectkey, bucketname))



if __name__ == '__main__':

    # Get and Print the list of user's environment variables 
    env_var = os.environ 
    print("\n User's Environment variables:") 
    pprint.pprint(dict(env_var), width = 1) 

    QUEUEURL = get_queuename()
    
    sqs_client = boto3.client('sqs')
    s3_client = boto3.client('s3')

    start_downloads(QUEUEURL, sqs_client, s3_client)
































