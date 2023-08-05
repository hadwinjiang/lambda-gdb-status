
mysql -hagora-kicking-uswest2.cluster-cfmlgwrkgd8f.us-west-2.rds.amazonaws.com -uadmin -pAdmin123 
use sbtest;

aws rds describe-db-cluster-endpoints --db-cluster-identifier agora-kicking-uswest1 --region us-west-1
{
    "DBClusterEndpoints": [
        {
            "Status": "inactive", 
            "Endpoint": "agora-kicking-uswest1.cluster-cxwjwjib0dud.us-west-1.rds.amazonaws.com", 
            "DBClusterIdentifier": "agora-kicking-uswest1", 
            "EndpointType": "WRITER"
        }, 
        {
            "Status": "available", 
            "Endpoint": "agora-kicking-uswest1.cluster-ro-cxwjwjib0dud.us-west-1.rds.amazonaws.com", 
            "DBClusterIdentifier": "agora-kicking-uswest1", 
            "EndpointType": "READER"
        }
    ]
}
aws rds describe-db-cluster-endpoints --db-cluster-identifier agora-kicking-uswest2 --region us-west-2
{
    "DBClusterEndpoints": [
        {
            "Status": "available", 
            "Endpoint": "agora-kicking-uswest2.cluster-cfmlgwrkgd8f.us-west-2.rds.amazonaws.com", 
            "DBClusterIdentifier": "agora-kicking-uswest2", 
            "EndpointType": "WRITER"
        }, 
        {
            "Status": "available", 
            "Endpoint": "agora-kicking-uswest2.cluster-ro-cfmlgwrkgd8f.us-west-2.rds.amazonaws.com", 
            "DBClusterIdentifier": "agora-kicking-uswest2", 
            "EndpointType": "READER"
        }
    ]
}

https://docs.aws.amazon.com/cli/latest/reference/stepfunctions/start-execution.html
aws stepfunctions start-execution --input "input": "{\"first_name\" : \"test\"}"

# reference documents:
https://docs.aws.amazon.com/lambda/latest/dg/services-rds-tutorial.html

EventBridge - Schedules 0 */6 * * ? *
