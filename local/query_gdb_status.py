import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')
useast1_client = boto3.client('rds', region_name="us-east-1")
uswest1_client = boto3.client('rds', region_name="us-west-1")
uswest2_client = boto3.client('rds', region_name="us-west-2")

def lambda_handler(event, context):
    # event content
    # {
    #   "endless": "Yes",
    #   "us-east-1": "agora-kicking-useast1",
    #   "us-west-1": "agora-kicking-uswest1",
    #   "us-west-2": "agora-kicking-uswest2",
    #   "region_id": "us-west-2"
    # }
    try:
        logger.info(event)
    
        report = {}
        useast1_response = useast1_client.describe_db_cluster_endpoints(
            DBClusterIdentifier=event["us-east-1"],    # Regional Cluster Identifier
        )
        report["us-east-1"]=useast1_response["DBClusterEndpoints"]
        
        uswest1_response = uswest1_client.describe_db_cluster_endpoints(
            DBClusterIdentifier=event["us-west-1"],    # Regional Cluster Identifier
        )
        report["us-west-1"]=uswest1_response["DBClusterEndpoints"]
        
        uswest2_response = uswest2_client.describe_db_cluster_endpoints(
            DBClusterIdentifier=event["us-west-2"],    # Regional Cluster Identifier
        )
        report["us-west-2"]=uswest2_response["DBClusterEndpoints"]
        return report
        
    except Exception as error:
        logger.info(error)
        return {}