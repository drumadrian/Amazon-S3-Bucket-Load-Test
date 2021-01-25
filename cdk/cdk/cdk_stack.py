from aws_cdk import core
import aws_cdk.aws_secretsmanager as aws_secretsmanager
import aws_cdk.aws_iam as aws_iam
import aws_cdk.aws_s3 as aws_s3
import aws_cdk.aws_elasticsearch as aws_elasticsearch
import aws_cdk.aws_ecr as aws_ecr
import aws_cdk.aws_logs as aws_logs
import aws_cdk.aws_route53 as aws_route53
from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as aws_ecs, aws_ecs_patterns as ecs_patterns)
import aws_cdk.aws_sqs as aws_sqs



###########################################################################
# References 
###########################################################################
# https://github.com/aws/aws-cdk/issues/7236


class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        ###########################################################################
        # AMAZON VPC  
        ###########################################################################
        vpc = ec2.Vpc(self, "LoadTestVPC", max_azs=3)     # default is all AZs in region


        ###########################################################################
        # AMAZON ECS Repositories  
        ###########################################################################
        # get_repository = aws_ecs.IRepository(self, "get_repository", image_scan_on_push=True, removal_policy=aws_cdk.core.RemovalPolicy("DESTROY") )
        # put_repository = aws_ecs.IRepository(self, "put_repository", image_scan_on_push=True, removal_policy=aws_cdk.core.RemovalPolicy("DESTROY") )
        get_repository = aws_ecr.Repository(self, "get_repository", image_scan_on_push=True, removal_policy=core.RemovalPolicy("DESTROY") )
        put_repository = aws_ecr.Repository(self, "put_repository", image_scan_on_push=True, removal_policy=core.RemovalPolicy("DESTROY") )
        xray_repository = aws_ecr.Repository(self, "xray_repository", image_scan_on_push=True, removal_policy=core.RemovalPolicy("DESTROY") )


        ###########################################################################
        # AMAZON ECS Roles and Policies
        ###########################################################################        
        task_execution_policy_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["logs:*", "ecs:*", "ec2:*", "elasticloadbalancing:*","ecr:*"],
            resources=["*"]
            )
        task_execution_policy_document = aws_iam.PolicyDocument()
        task_execution_policy_document.add_statements(task_execution_policy_statement)
        task_execution_policy = aws_iam.Policy(self, "task_execution_policy", document=task_execution_policy_document)
        task_execution_role = aws_iam.Role(self, "task_execution_role", assumed_by=aws_iam.ServicePrincipal('ecs-tasks.amazonaws.com') )
        task_execution_role.attach_inline_policy(task_execution_policy)

        task_policy_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["logs:*", "xray:*", "sqs:*", "s3:*"],
            resources=["*"]
            )
        task_policy_document = aws_iam.PolicyDocument()
        task_policy_document.add_statements(task_policy_statement)
        task_policy = aws_iam.Policy(self, "task_policy", document=task_policy_document)
        task_role = aws_iam.Role(self, "task_role", assumed_by=aws_iam.ServicePrincipal('ecs-tasks.amazonaws.com') )
        task_role.attach_inline_policy(task_policy)


        ###########################################################################
        # AMAZON ECS Task definitions
        ###########################################################################
        get_task_definition = aws_ecs.TaskDefinition(self, "gettaskdefinition",
                                                                        compatibility=aws_ecs.Compatibility("FARGATE"), 
                                                                        cpu="1024", 
                                                                        # ipc_mode=None, 
                                                                        memory_mib="2048", 
                                                                        network_mode=aws_ecs.NetworkMode("AWS_VPC"), 
                                                                        # pid_mode=None,                                      #Not supported in Fargate and Windows containers
                                                                        # placement_constraints=None, 
                                                                        execution_role=task_execution_role, 
                                                                        # family=None, 
                                                                        # proxy_configuration=None, 
                                                                        task_role=task_role
                                                                        # volumes=None
                                                                        )

        put_task_definition = aws_ecs.TaskDefinition(self, "puttaskdefinition",
                                                                        compatibility=aws_ecs.Compatibility("FARGATE"), 
                                                                        cpu="1024", 
                                                                        # ipc_mode=None, 
                                                                        memory_mib="2048", 
                                                                        network_mode=aws_ecs.NetworkMode("AWS_VPC"), 
                                                                        # pid_mode=None,                                      #Not supported in Fargate and Windows containers
                                                                        # placement_constraints=None, 
                                                                        execution_role=task_execution_role, 
                                                                        # family=None, 
                                                                        # proxy_configuration=None, 
                                                                        task_role=task_role
                                                                        # volumes=None
                                                                        )


        ###########################################################################
        # AMAZON S3 BUCKETS 
        ###########################################################################
        storage_bucket = aws_s3.Bucket(self, "storage_bucket")


        ###########################################################################
        # AWS SQS QUEUES
        ###########################################################################
        ecs_task_queue_iqueue = aws_sqs.Queue(self, "ecs_task_queue_iqueue_dlq")
        ecs_task_queue_queue_dlq = aws_sqs.DeadLetterQueue(max_receive_count=10, queue=ecs_task_queue_iqueue)
        ecs_task_queue_queue = aws_sqs.Queue(self, "ecs_task_queue_queue", visibility_timeout=core.Duration.seconds(300), dead_letter_queue=ecs_task_queue_queue_dlq)


        ###########################################################################
        # AMAZON ECS Images 
        ###########################################################################
        get_repository_ecr_image = aws_ecs.EcrImage(repository=get_repository, tag="latest")
        put_repository_ecr_image = aws_ecs.EcrImage(repository=put_repository, tag="latest")
        xray_repository_ecr_image = aws_ecs.EcrImage(repository=xray_repository, tag="latest")
        environment_variables = {}
        environment_variables["SQS_QUEUE"] = ecs_task_queue_queue.queue_url
        environment_variables["S3_BUCKET"] = storage_bucket.bucket_name
        
        get_task_log_driver = aws_ecs.LogDriver.aws_logs(stream_prefix="S3LoadTest", log_retention=aws_logs.RetentionDays("ONE_WEEK"))
        put_task_log_driver = aws_ecs.LogDriver.aws_logs(stream_prefix="S3LoadTest", log_retention=aws_logs.RetentionDays("ONE_WEEK"))
        xray_task_log_driver = aws_ecs.LogDriver.aws_logs(stream_prefix="S3LoadTest", log_retention=aws_logs.RetentionDays("ONE_WEEK"))


        get_task_definition.add_container("get_task_definition_get", 
                                                    image=get_repository_ecr_image, 
                                                    memory_reservation_mib=1024,
                                                    environment=environment_variables,
                                                    logging=get_task_log_driver
                                                    )
        get_task_definition.add_container("get_task_definition_xray", 
                                                    image=xray_repository_ecr_image, 
                                                    memory_reservation_mib=1024,
                                                    environment=environment_variables,
                                                    logging=xray_task_log_driver
                                                    )

        put_task_definition.add_container("put_task_definition_put", 
                                                    image=put_repository_ecr_image, 
                                                    memory_reservation_mib=1024,
                                                    environment=environment_variables,
                                                    logging=put_task_log_driver
                                                    )
        put_task_definition.add_container("put_task_definition_xray", 
                                                    image=xray_repository_ecr_image, 
                                                    memory_reservation_mib=1024,
                                                    environment=environment_variables,
                                                    logging=xray_task_log_driver
                                                    )


        ###########################################################################
        # AMAZON ECS CLUSTER 
        ###########################################################################
        cluster = aws_ecs.Cluster(self, "LoadTestCluster", vpc=vpc)


        ###########################################################################
        # AWS ROUTE53 HOSTED ZONE 
        ###########################################################################
        hosted_zone = aws_route53.HostedZone(self, "hosted_zone", zone_name="loadtest.com" ,comment="private hosted zone for loadtest system")
        hosted_zone.add_vpc(vpc)
        bucket_record_values = [storage_bucket.bucket_name]
        queue_record_values = [ecs_task_queue_queue.queue_url]
        bucket_record_name = "bucket." + hosted_zone.zone_name
        queue_record_name = "filesqueue." + hosted_zone.zone_name
        hosted_zone_record_bucket = aws_route53.TxtRecord(self, "hosted_zone_record_bucket", record_name=bucket_record_name, values=bucket_record_values, zone=hosted_zone, comment="dns record for bucket name")
        hosted_zone_record_queue = aws_route53.TxtRecord(self, "hosted_zone_record_queue", record_name=queue_record_name, values=queue_record_values, zone=hosted_zone, comment="dns record for queue name")







