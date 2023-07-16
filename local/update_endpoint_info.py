import sys
import logging
import pymysql
import json
import os

# rds settings
# user_name = os.environ['USER_NAME']
# password = os.environ['PASSWORD']
# db_name = os.environ['DB_NAME']
user_name = 'admin'
password = 'Admin123'
db_name = 'sbtest'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def build_sql(region_id, endpoints_json, history_table=False):
    writer_endpoint_json = [endpoint for endpoint in endpoints_json if(endpoint['EndpointType'] == 'WRITER')][0]
    reader_endpoint_json = [endpoint for endpoint in endpoints_json if(endpoint['EndpointType'] == 'READER')][0]
    writer_endpoint = writer_endpoint_json['Endpoint']
    writer_status = writer_endpoint_json['Status']
    reader_endpoint = reader_endpoint_json['Endpoint']
    reader_status = reader_endpoint_json['Status']
    if history_table:
        sql = f'''insert into endpoint_history 
        (region_id, query_time, 
        writer_endpoint, writer_status, reader_endpoint, reader_status) 
        values("{region_id}", NOW(), "{writer_endpoint}", "{writer_status}", "{reader_endpoint}", "{reader_status}") '''
    else:
        sql = f'''insert into endpoint 
        (region_id, query_time, 
        writer_endpoint, writer_status, reader_endpoint, reader_status) 
        values("{region_id}", NOW(), "{writer_endpoint}", "{writer_status}", "{reader_endpoint}", "{reader_status}") 
        ON DUPLICATE KEY UPDATE query_time=NOW(),
        writer_endpoint="{writer_endpoint}", writer_status="{writer_status}", 
        reader_endpoint="{reader_endpoint}", reader_status="{reader_status}" '''
    return sql

def lambda_handler(event, context):
    
    try:
        local_region_id = event["region_id"]
        query_result = event["query_result"]["Payload"]
    
        endpoints = query_result[local_region_id]
        region_writer_endpoint_json = [endpoint for endpoint in endpoints if(endpoint['EndpointType'] == 'WRITER')][0]
        logger.info(region_writer_endpoint_json)
        region_reader_endpoint_json = [endpoint for endpoint in endpoints if(endpoint['EndpointType'] == 'READER')][0]
        logger.info(region_reader_endpoint_json)
        
        region_writer_status = region_writer_endpoint_json['Status']
        region_endpoint = region_writer_endpoint_json['Endpoint'] if region_writer_status == 'available' else region_reader_endpoint_json['Endpoint'] 
        logger.info(region_endpoint)
        logger.info(region_writer_status)
        
        rds_host = region_endpoint
        
        if region_writer_status == 'available':
            conn = pymysql.connect(host=rds_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
        else:
            logger.info("set aurora_replica_read_consistency = 'eventual';")
            conn = pymysql.connect(host=rds_host, user=user_name, passwd=password, db=db_name, connect_timeout=5, init_command="set aurora_replica_read_consistency = 'eventual'")
            
        useast1_sql_string = build_sql('us-east-1', query_result['us-east-1'])
        uswest1_sql_string = build_sql('us-west-1', query_result['us-west-1'])
        uswest2_sql_string = build_sql('us-west-2', query_result['us-west-2'])
        history_string = build_sql(local_region_id, query_result[local_region_id], history_table=True)
    
        with conn.cursor() as cur:
            # cur.execute(f'''create table if not exists endpoint ( 
            # region_id varchar(20) NOT NULL, 
            # query_time datetime,
            # writer_endpoint varchar(255) NOT NULL, 
            # writer_status varchar(20), 
            # reader_endpoint varchar(255) NOT NULL, 
            # reader_status varchar(20), 
            # PRIMARY KEY (region_id))''')
            
            # cur.execute(f'''create table if not exists endpoint_history ( 
            # region_id varchar(20) NOT NULL, 
            # query_time datetime,
            # writer_endpoint varchar(255) NOT NULL, 
            # writer_status varchar(20), 
            # reader_endpoint varchar(255) NOT NULL, 
            # reader_status varchar(20))''')
                
            cur.execute(useast1_sql_string)
            cur.execute(uswest1_sql_string)
            cur.execute(uswest2_sql_string)
            
            cur.execute(history_string)
        conn.commit()
    
        return "Success"

    except Exception as e:
        logger.error("Unexpected Error")
        logger.error(e)
        return "Failed"

    
    