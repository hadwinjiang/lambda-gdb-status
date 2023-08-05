import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import * as sfn from "aws-cdk-lib/aws-stepfunctions";
import * as tasks from "aws-cdk-lib/aws-stepfunctions-tasks";
import { Construct } from 'constructs';

export class CdkStoreStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // define how frequent the endpoints information would be queried and updated.
    const repeatBySeconds = 10;

    // lambda to query global database status
    const queryGlobalDatabaseStatusLambda = new lambda.Function(this, 'QueryGlobalDatabaseStatus', {
      code: lambda.Code.fromAsset('lambda-query-gdb-status'),
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: "query_gdb_status.lambda_handler",
      timeout: Duration.seconds(300),
    });
    queryGlobalDatabaseStatusLambda.role?.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonRDSFullAccess'));

    // lambda to update endpoints information
    const updateEndpointsInforLambda = new lambda.Function(this, 'UpdateEndpointsInfor', {
      code: lambda.Code.fromAsset('lambda-update-endpoints-info',  {
        bundling: {
          image: lambda.Runtime.PYTHON_3_9.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      environment: {
        "USER_NAME": "admin",
        "PASSWORD": "Admin123",
        "DB_NAME": "sbtest",
      },
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: "query_gdb_status.lambda_handler",
      timeout: Duration.seconds(180),
    });

    // step function definition

    const callQueryGDBOnce = new tasks.LambdaInvoke(this, 'query_once', {
      lambdaFunction: queryGlobalDatabaseStatusLambda,
      resultPath: '$.query_result'
    });

    const callUpdateEndpointInfoOnce = new tasks.LambdaInvoke(this, 'update_once', {
      lambdaFunction: updateEndpointsInforLambda,
      resultPath: '$.update_result'
    });

    const loopQueryGDBStatus = new tasks.LambdaInvoke(this, 'query_gdb', {
      lambdaFunction: queryGlobalDatabaseStatusLambda,
      resultPath: '$.query_result'
    });

    const loopUpdateEndpointInfo = new tasks.LambdaInvoke(this, 'update_endpoint', {
      lambdaFunction: updateEndpointsInforLambda,
      resultPath: '$.update_result'
    });

    const waitTime = Duration.seconds(repeatBySeconds);
    const repeatX = new sfn.Wait(this, 'Wait X Seconds', {
      time: sfn.WaitTime.duration(waitTime)
    });
    const repeatTask = repeatX.next(loopQueryGDBStatus);

    // Whole workflow definition
    const definition = new sfn.Choice(this, 'repeat "Query & Update"?')
      .when(sfn.Condition.stringEquals('$.endless', 'No'), callQueryGDBOnce.next(callUpdateEndpointInfoOnce).next(new sfn.Succeed(this, "Sucess")))
      .otherwise(loopQueryGDBStatus.next(loopUpdateEndpointInfo).next(repeatTask));

    const stateMachine = new sfn.StateMachine(this, 'QueryGDBAndUpdate', {
      definition
    });
  }
}