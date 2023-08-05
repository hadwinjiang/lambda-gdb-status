import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import { Construct } from 'constructs';

export class CdkStoreStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

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
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: "query_gdb_status.lambda_handler",
      timeout: Duration.seconds(300),
    });
    

  }
}
