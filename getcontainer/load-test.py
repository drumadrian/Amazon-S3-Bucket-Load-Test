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


################################################################################################################
#   Download files continuously from S3
################################################################################################################
def start_downloads(QUEUEURL, sqs_client, s3_client, sdk):
    while True:

        now = datetime.now() # current date and time
        time_now = now.strftime("%H:%M:%S.%f")
        print("\n In start_downloads() Time now: " + time_now)

        with sdk.trace_custom_service('dequeue_message()', 'SQS'):
            message = dequeue_message(QUEUEURL, sqs_client)
        print("\n message={0}\n".format(message))

        bucketname = message[0]
        objectkey = message[1]

        with sdk.trace_custom_service('get_object()', 'S3'):
            if bucketname != "wait":
                try:
                    get_object_response = s3_client.get_object(
                        Bucket=bucketname,
                        Key=objectkey
                    )
                except ClientError as e:
                    print("Error downloading object: {0} from bucket: {1}".format(objectkey, bucketname))


################################################################################################################
#   Debug Dynatrace SDK errors
################################################################################################################
def _diag_callback(unicode_message):
	print(unicode_message)


################################################################################################################
#   Main function 
################################################################################################################
if __name__ == '__main__':

    try:
        ################################################################################################################
        #   Setup Dynatrace Tracing
        ################################################################################################################
        init_result = oneagent.initialize()
        # if not oneagent.initialize():
        if not init_result:
            print('Error initializing OneAgent SDK.')
        if init_result:
            print('SDK should work (but agent might be inactive).')
            print('OneAgent SDK initialization result: ' + repr(init_result))
        else:
            print('SDK will definitely not work (i.e. functions will be no-ops):', init_result)
        sdk = oneagent.get_sdk()
        if sdk.agent_state not in (AgentState.ACTIVE, AgentState.TEMPORARILY_INACTIVE):
            print('Dynatrace SDK agent is NOT Active, you will not see data from this process.')
        sdk.set_diagnostic_callback(_diag_callback)
        print('It may take a few moments before the path appears in the UI.')
        ################################################################################################################


        ################################################################################################################
        # Get and Print the list of user's environment variables 
        env_var = os.environ 
        print("\n User's Environment variables:") 
        pprint.pprint(dict(env_var), width = 1) 
        ################################################################################################################

        ################################################################################################################
        sdk.add_custom_request_attribute('Method', 'get_queuename()')
        sdk.add_custom_request_attribute('Container', 'Put')
        sdk.add_custom_request_attribute('famous actor', 'Benedict Cumberbatch')
        with sdk.trace_custom_service('get_queuename()', 'DNS'):
            QUEUEURL = get_queuename()
        # QUEUEURL = "https://sqs.us-west-2.amazonaws.com/696965430582/S3LoadTest-ecstaskqueuequeue6E80C2CD-14EYBYEKSI2FE"
        ################################################################################################################

        ################################################################################################################
        sqs_client = boto3.client('sqs')
        s3_client = boto3.client('s3')
        start_downloads(QUEUEURL, sqs_client, s3_client, sdk)
        ################################################################################################################

    finally:
        shutdown_error = oneagent.shutdown()
        if shutdown_error:
            print('Error shutting down SDK:', shutdown_error)






