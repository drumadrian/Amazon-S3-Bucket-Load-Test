import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime


def upload_to_bucket(local_file, bucket, s3_file):
    s3 = boto3.client('s3')

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


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

var=0
while var < 100:
# while True:
    now = datetime.now() # current date and time
    print(now)
    # s3_file_name="diagram_" + now.strftime("%H:%M:%S:%f") + ".png"
    s3_file_name=now.strftime("%f_%H:%M:%S:%f") + "_diagram" + ".png"
    print(s3_file_name)
    uploaded = upload_to_bucket('/home/ec2-user/environment/Amazon-S3-Bucket-Load-Test/container/diagram.png', 'amazon-s3-bucket-load-test-storagebucket-knlgpd3wpz0n', s3_file_name)
    done = datetime.now()
    # uploaded = upload_to_bucket('/beef/diagram.png', 'amazon-s3-bucket-load-test-storagebucket-knlgpd3wpz0n', s3_file_name)
    var = var + 1
    
