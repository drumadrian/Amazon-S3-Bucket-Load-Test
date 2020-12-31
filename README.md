# AWS S3 Bucket Load Testing

Purpose: Create and Put files into a single S3 bucket as fast as possible. 

![MacDown logo](S3_Load_Test_Diagram.png)

## Summary

The goal is to create as many files as specified, then copy them into Amazon S3 using a python script running in a Fargate Task. 


Steps: 

These steps are guidance and can be executed out of order by an experienced operator:

* Bootstrap your AWS Account for the CDK
* Deploy the cdk stack using `cdk deploy` 
* Create the containers needed using the included Dockerfiles
* Push the containers to the matching ECR repo
* Put the bucket name of the newly created bucket in a DNS TXT entry
* Deploy the Fargate application and monitor X-Ray, CloudWatch metrics, and CloudWatch logs

</br>


### Commands to Build container zip file: 
###### (to be uploaed to S3 for container build pipeline):

```

cd Amazon-S3-Bucket-Load-Test

GET_REPOSITORY_NAME=getrepositorya5f65c8e-opes9uqkcxi1
GET_REPOSITORY_URI=696965430582.dkr.ecr.us-west-2.amazonaws.com/getrepositorya5f65c8e-opes9uqkcxi1
AWS_REGION=us-west-2

echo $GET_REPOSITORY_NAME
echo $GET_REPOSITORY_URI
echo $AWS_REGION


cd getcontainer
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $GET_REPOSITORY_URI
docker build -t $GET_REPOSITORY_NAME:latest .
docker tag $GET_REPOSITORY_NAME:latest $GET_REPOSITORY_URI:latest
docker push $GET_REPOSITORY_URI:latest
cd ..



PUT_REPOSITORY_NAME=putrepositoryadbc1150-wtujtmuva7bf
PUT_REPOSITORY_URI=696965430582.dkr.ecr.us-west-2.amazonaws.com/putrepositoryadbc1150-wtujtmuva7bf
AWS_REGION=us-west-2

echo $PUT_REPOSITORY_NAME
echo $PUT_REPOSITORY_URI
echo $AWS_REGION

cd putcontainer
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $PUT_REPOSITORY_URI
docker build -t $PUT_REPOSITORY_NAME:latest .
docker tag $PUT_REPOSITORY_NAME:latest $PUT_REPOSITORY_URI:latest
docker push $PUT_REPOSITORY_URI:latest
cd ..




XRAY_REPOSITORY_NAME=xrayrepository855dc8d2-fy0wax3vgbhl
XRAY_REPOSITORY_URI=696965430582.dkr.ecr.us-west-2.amazonaws.com/xrayrepository855dc8d2-fy0wax3vgbhl
AWS_REGION=us-west-2

echo $XRAY_REPOSITORY_NAME
echo $XRAY_REPOSITORY_URI
echo $AWS_REGION

cd xraycontainer
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $XRAY_REPOSITORY_URI
docker build -t $XRAY_REPOSITORY_NAME:latest .
docker tag $XRAY_REPOSITORY_NAME:latest $XRAY_REPOSITORY_URI:latest
docker push $XRAY_REPOSITORY_URI:latest
cd ..




```

### CLI Commands to Deploy Solution: 

```
cdk bootstrap
cdk deploy
```


### How to Test:




### References:

https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python

https://stackoverflow.com/questions/14275975/creating-random-binary-files

http://ls.pwd.io/2013/06/parallel-s3-uploads-using-boto-and-threads-in-python/

https://docs.aws.amazon.com/AmazonS3/latest/user-guide/empty-bucket.html

https://docs.aws.amazon.com/AmazonS3/latest/user-guide/configure-metrics.html



