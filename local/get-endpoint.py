import json
import boto3

print('Loading function')
rds_client = boto3.client('rds')
aurora_client = boto3.client('rds-data')

response = rds_client.describe_db_cluster_endpoints(
    DBClusterIdentifier='agora-kicking-uswest2',    # Regional Cluster Identifier
)



for item in response['DBClusterEndpoints']:
    if item['EndpointType'] == 'WRITER':
        writer_endpoint = item['Endpoint']
        writer_status = item['Status']
        print("writer_endpoint:", writer_endpoint)
        print("writer_status:", writer_status)
    else:
        readonly_endpoint = item['Endpoint']
        readonly_status = item['Status']
        print("readonly_endpoint:", readonly_endpoint)
        print("readonly_status:", readonly_status)

if writer_status == 'available':
    print("Writing to writer endpoint:", writer_endpoint)
    # insert a row into aurora table

else:
    print("Writing forward to readonly endpoint:", readonly_endpoint)
