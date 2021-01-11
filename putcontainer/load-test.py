import boto3
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import ClientError
from datetime import datetime
import dns.resolver
import os 
import pprint
import json 
import time
import oneagent



################################################################################################################
#   Get the queue name to enqueue messages 
################################################################################################################
def get_queuename():
    bytes_response = dns.resolver.query("filesqueue.loadtest.com","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("\n filesqueue.loadtest.com= {0}\n".format(response))
    print(response)
    return response

################################################################################################################
#   Get bucketname using DNS TXT record 
################################################################################################################
def get_bucketname():
    bytes_response = dns.resolver.query("bucket.loadtest.com","TXT").response.answer[0][-1].strings[0]
    response = bytes_response.decode("utf-8")
    print("\n bucket.loadtest.com= {0}\n".format(response))
    return response

################################################################################################################
#   Upload the local file to the bucket 
################################################################################################################
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



################################################################################################################
#   enqueue a message onto the SQS queue
################################################################################################################
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



################################################################################################################
#   Upload files continuously to S3
################################################################################################################
def start_uploads(bucketname, queueURL, sqs_client):
    var=0
    # for var in range(OBJECTS_PER_CONTAINER):
    while True:

        now = datetime.now() # current date and time
        print("\n Time now: " + now.strftime("%H:%M:%S.%f"))

        # s3_file_name="diagram_" + now.strftime("%H:%M:%S.%f") + ".png"
        s3_file_name=now.strftime("%f_%H:%M:%S.%f") + "_diagram" + ".png"
        print("\n s3_file_name: {0}\n".format(s3_file_name))

        # Start a subsegment for upload_to_bucket()
        subsegment = xray_recorder.begin_subsegment('function: upload_to_bucket')
        uploaded = upload_to_bucket('/app/diagram.png', bucketname, s3_file_name)
        # uploaded = upload_to_bucket('diagram.png', bucketname, s3_file_name)
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


################################################################################################################
#   Main function 
################################################################################################################
if __name__ == '__main__':

    try:
        ################################################################################################################
        #   Global Config settings
        ################################################################################################################
        OBJECTS_PER_CONTAINER = "∞"

        if not oneagent.initialize():
            print('Error initializing OneAgent SDK.')

        with oneagent.get_sdk().trace_incoming_remote_call('method', 'service', 'endpoint'):
            # pass
            # my code goes here? 

            print('It may take a few moments before the path appears in the UI.')

            # Start a segment
            # now = datetime.now() # current date and time

            # Get and Print the list of user's environment variables 
            env_var = os.environ 
            print("\n User's Environment variables:") 
            pprint.pprint(dict(env_var), width = 1) 

            # Start a subsegment for function: get_queuename 
            QUEUEURL = get_queuename()

            # Start a subsegment for function: get_bucketname 
            BUCKETNAME = get_bucketname()
            
            sqs_client = boto3.client('sqs')
            start_uploads(BUCKETNAME, QUEUEURL, sqs_client)

    finally:
        shutdown_error = oneagent.shutdown()
        if shutdown_error:
            print('Error shutting down SDK:', shutdown_error)


    # # Close the segment
    # oneagent.shutdown()








################################################################################################################
#   Unused Code 
################################################################################################################
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



