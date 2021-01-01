from aws_cdk import core
import aws_cdk.aws_secretsmanager as aws_secretsmanager
# import aws_cdk.aws_cloudformation as aws_cloudformation
# import aws_cdk.aws_lambda as aws_lambda
# from aws_cdk.core import CustomResource
import aws_cdk.aws_iam as aws_iam
# import aws_cdk.aws_s3_notifications as aws_s3_notifications
import aws_cdk.aws_s3 as aws_s3
# import aws_cdk.aws_sns as aws_sns
# import aws_cdk.aws_sns_subscriptions as aws_sns_subscriptions
# from aws_cdk.aws_lambda_event_sources import SqsEventSource
import aws_cdk.aws_elasticsearch as aws_elasticsearch
# import aws_cdk.aws_cognito as aws_cognito
# import aws_cdk.aws_elasticloadbalancingv2 as aws_elasticloadbalancingv2
# import aws_cdk.aws_ec2 as aws_ec2
import aws_cdk.aws_ecr as aws_ecr
# import aws_cdk.aws_cloudtrail as aws_cloudtrail
# import inspect as inspect
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
        # cloudtrail_log_bucket = aws_s3.Bucket(self, "cloudtrail_log_bucket")


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
        
        # get_task_log_driver = aws_ecs.LogDriver(self, container_definition=get_task_definition)
        # put_task_log_driver = aws_ecs.LogDriver(self, container_definition=put_task_definition)
        # xray_task_log_driver = aws_ecs.LogDriver(self, container_definition=xray_task_definition)

        # get_task_log_driver = aws_ecs.LogDriver()
        # put_task_log_driver = aws_ecs.LogDriver()
        # xray_task_log_driver = aws_ecs.LogDriver()
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
        # task_image = ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
        # ecs_patterns.QueueProcessingFargateService(self, "MyFargateService",
        #     cluster=cluster,            # Required
        #     cpu=512,                    # Default is 256
        #     desired_task_count=1,            # Default is 1
        #     image=task_image,
        #     memory_limit_mib=2048)      # Default is 512


        ###########################################################################
        # AWS SECRETS MANAGER - Templated secret 
        ###########################################################################
        templated_secret = aws_secretsmanager.Secret(self, "TemplatedSecret",
            description="Credentials and settings for configuration",
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template= "{\"username\":\"cleanbox\"}",
                generate_string_key="password"
            )
        )


        ###########################################################################
        # AWS ELASTICSEARCH DOMAIN ACCESS POLICY 
        ###########################################################################
        # this_aws_account = aws_iam.AccountPrincipal(account_id="012345678912")

        # s3_loadtest_logs_domain_domain_access_policy_statement = aws_iam.PolicyStatement(
        #     principals=[this_aws_account],
        #     effect=aws_iam.Effect.ALLOW,
        #     actions=["es:*"],
        #     resources=["*"]
        #     )

        # s3_loadtest_logs_domain_domain_access_policy_statement_list=[]
        # s3_loadtest_logs_domain_domain_access_policy_statement_list.append(s3_loadtest_logs_domain_domain_access_policy_statement)


        ###########################################################################
        # AWS ELASTICSEARCH DOMAIN
        ###########################################################################
        s3_loadtest_logs_domain = aws_elasticsearch.Domain(self, "s3_loadtest_logs_domain",
            version=aws_elasticsearch.ElasticsearchVersion.V7_1,
            capacity={
                "master_nodes": 3,
                "data_nodes": 4
            },
            ebs={
                "volume_size": 100
            },
            zone_awareness={
                "availability_zone_count": 2
            },
            logging={
                "slow_search_log_enabled": True,
                "app_log_enabled": True,
                "slow_index_log_enabled": True
            }
        )





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





























        # sqs_to_elasticsearch_service_queue_iqueue = aws_sqs.Queue(self, "sqs_to_elasticsearch_service_queue_dlq")
        # sqs_to_elasticsearch_service_queue_dlq = aws_sqs.DeadLetterQueue(max_receive_count=10, queue=sqs_to_elasticsearch_service_queue_iqueue)
        # sqs_to_elasticsearch_service_queue = aws_sqs.Queue(self, "sqs_to_elasticsearch_service_queue", visibility_timeout=core.Duration.seconds(300), dead_letter_queue=sqs_to_elasticsearch_service_queue_dlq)

        # sqs_to_elastic_cloud_queue_iqueue = aws_sqs.Queue(self, "sqs_to_elastic_cloud_queue_dlq")
        # sqs_to_elastic_cloud_queue_dlq = aws_sqs.DeadLetterQueue(max_receive_count=10, queue=sqs_to_elastic_cloud_queue_iqueue)
        # sqs_to_elastic_cloud_queue = aws_sqs.Queue(self, "sqs_to_elastic_cloud_queue", visibility_timeout=core.Duration.seconds(300), dead_letter_queue=sqs_to_elastic_cloud_queue_dlq)





        ###########################################################################
        # CUSTOM CLOUDFORMATION RESOURCE 
        ###########################################################################
        # customlambda = aws_lambda.Function(self,'customconfig',
        # handler='customconfig.on_event',
        # runtime=aws_lambda.Runtime.PYTHON_3_7,
        # code=aws_lambda.Code.asset('customconfig'),
        # )

        # customlambda_statement = aws_iam.PolicyStatement(actions=["events:PutRule"], conditions=None, effect=None, not_actions=None, not_principals=None, not_resources=None, principals=None, resources=["*"], sid=None)
        # customlambda.add_to_role_policy(statement=customlambda_statement)

        # my_provider = cr.Provider(self, "MyProvider",
        #     on_event_handler=customlambda,
        #     # is_complete_handler=is_complete, # optional async "waiter"
        #     log_retention=logs.RetentionDays.SIX_MONTHS
        # )

        # CustomResource(self, 'customconfigresource', service_token=my_provider.service_token)


        ###########################################################################
        # AWS LAMBDA FUNCTIONS 
        ###########################################################################
        # sqs_to_elastic_cloud = aws_lambda.Function(self,'sqs_to_elastic_cloud',
        # handler='sqs_to_elastic_cloud.lambda_handler',
        # runtime=aws_lambda.Runtime.PYTHON_3_7,
        # code=aws_lambda.Code.asset('sqs_to_elastic_cloud'),
        # memory_size=4096,
        # timeout=core.Duration.seconds(300)
        # )

        # sqs_to_elasticsearch_service = aws_lambda.Function(self,'sqs_to_elasticsearch_service',
        # handler='sqs_to_elasticsearch_service.lambda_handler',
        # runtime=aws_lambda.Runtime.PYTHON_3_7,
        # code=aws_lambda.Code.asset('sqs_to_elasticsearch_service'),
        # memory_size=4096,
        # timeout=core.Duration.seconds(300)
        # )
        ###########################################################################
        # AWS LAMBDA FUNCTIONS 
        ###########################################################################



        ###########################################################################
        # LAMBDA SUPPLEMENTAL POLICIES 
        ###########################################################################
        # lambda_supplemental_policy_statement = aws_iam.PolicyStatement(
        #     effect=aws_iam.Effect.ALLOW,
        #     actions=["s3:Get*","s3:Head*","s3:List*","firehose:*","es:*"],
        #     resources=["*"]
        #     )

        # sqs_to_elastic_cloud.add_to_role_policy(lambda_supplemental_policy_statement)
        # sqs_to_elasticsearch_service.add_to_role_policy(lambda_supplemental_policy_statement)
        ###########################################################################
        # AWS SNS TOPICS 
        ###########################################################################
        # cloudtrail_log_topic = aws_sns.Topic(self, "cloudtrail_log_topic")


        ###########################################################################
        # ADD AMAZON S3 BUCKET NOTIFICATIONS
        ###########################################################################
        # cloudtrail_log_bucket.add_event_notification(aws_s3.EventType.OBJECT_CREATED, aws_s3_notifications.SnsDestination(cloudtrail_log_topic))



        ###########################################################################
        # AWS SNS TOPIC SUBSCRIPTIONS
        ###########################################################################
        # cloudtrail_log_topic.add_subscription(aws_sns_subscriptions.SqsSubscription(sqs_to_elastic_cloud_queue))
        # cloudtrail_log_topic.add_subscription(aws_sns_subscriptions.SqsSubscription(sqs_to_elasticsearch_service_queue))

        
        ###########################################################################
        # AWS LAMBDA SQS EVENT SOURCE
        ###########################################################################
        # sqs_to_elastic_cloud.add_event_source(SqsEventSource(sqs_to_elastic_cloud_queue,batch_size=10))
        # sqs_to_elasticsearch_service.add_event_source(SqsEventSource(sqs_to_elasticsearch_service_queue,batch_size=10))



        ###########################################################################
        # AMAZON COGNITO USER POOL
        ###########################################################################
        # s3_to_elasticsearch_user_pool = aws_cognito.UserPool(self, "s3-to-elasticsearch-cloudtrial-logs-pool",
        #                                                     account_recovery=None, 
        #                                                     auto_verify=None, 
        #                                                     custom_attributes=None, 
        #                                                     email_settings=None, 
        #                                                     enable_sms_role=None, 
        #                                                     lambda_triggers=None, 
        #                                                     mfa=None, 
        #                                                     mfa_second_factor=None, 
        #                                                     password_policy=None, 
        #                                                     self_sign_up_enabled=None, 
        #                                                     sign_in_aliases=aws_cognito.SignInAliases(email=True, phone=None, preferred_username=None, username=True), 
        #                                                     sign_in_case_sensitive=None, 
        #                                                     sms_role=None, 
        #                                                     sms_role_external_id=None, 
        #                                                     standard_attributes=None, 
        #                                                     user_invitation=None, 
        #                                                     user_pool_name=None, 
        #                                                     user_verification=None
        #                                                     )


        # sqs_to_elasticsearch_service.add_environment("ELASTICSEARCH_HOST", s3_to_elasticsearch_cloudtrail_logs_domain.domain_endpoint )
        # sqs_to_elasticsearch_service.add_environment("QUEUEURL", sqs_to_elasticsearch_service_queue.queue_url )
        # sqs_to_elasticsearch_service.add_environment("DEBUG", "False" )

        # sqs_to_elastic_cloud.add_environment("ELASTICCLOUD_SECRET_NAME", "-")
        # sqs_to_elastic_cloud.add_environment("ELASTIC_CLOUD_ID", "-")
        # sqs_to_elastic_cloud.add_environment("ELASTIC_CLOUD_PASSWORD", "-")
        # sqs_to_elastic_cloud.add_environment("ELASTIC_CLOUD_USERNAME", "-")
        # sqs_to_elastic_cloud.add_environment("QUEUEURL", sqs_to_elastic_cloud_queue.queue_url )
        # sqs_to_elastic_cloud.add_environment("DEBUG", "False" )



        ###########################################################################
        # AWS COGNITO USER POOL
        ###########################################################################
        # allevents_trail = aws_cloudtrail.Trail(self, "allevents_trail", bucket=cloudtrail_log_bucket, 
        #                                                                 cloud_watch_log_group=None, 
        #                                                                 cloud_watch_logs_retention=None, 
        #                                                                 enable_file_validation=None, 
        #                                                                 encryption_key=None, 
        #                                                                 include_global_service_events=None, 
        #                                                                 is_multi_region_trail=True, 
        #                                                                 kms_key=None, 
        #                                                                 management_events=aws_cloudtrail.ReadWriteType("ALL"), 
        #                                                                 s3_key_prefix=None, 
        #                                                                 send_to_cloud_watch_logs=False, 
        #                                                                 sns_topic=None, 
        #                                                                 trail_name=None)



