import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):

    try:
        # Get the cell id and URLs from the event
        if (event['body']) and (event['body'] is not None):
            body = json.loads(event['body'])
            if (body['cellId']) and (body['cellId'] is not None):
                cellId = body['cellId']
            if (body['cellUrl']) and (body['cellUrl'] is not None):
                cellUrl = body['cellUrl']
            if (body['cellUrl2']) and (body['cellUrl2'] is not None):
                cellUrl2 = body['cellUrl2']

        
        # Perform cross-reference and health check
        response = validate_cell_urls(cellId, cellUrl, cellUrl2)

        # Return the status of the URLs
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:
        # Return an error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def validate_cell_urls(cell_id, cell_url_1, cell_url_2):

    try:
        
        table_name = 'tbl_router'
        sort_key = 'cellId'
        gsi_name = 'marketId-currentCapacity-index'
        cell_urls = []  # string array containing received cell urls from client
        cell_endpoints = [] # string array containing cell urls stored in the DB
        cell_urls.append(cell_url_1)
        cell_urls.append(cell_url_2)
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Get endpoint of the cell from the DB
        
        response = table.query(
            ProjectionExpression='cellId,endPoint_1,endPoint_2,isHealthy',
            KeyConditionExpression= Key('marketId').eq('europe') & Key('cellId').eq(cell_id)
            )
            
        if 'Items' in response and len(response['Items']) > 0:
            record= response['Items'][0]
            cell_endpoints.append(record.get('endPoint_1'))
            cell_endpoints.append(record.get('endPoint_2'))
            is_healthy= record.get('isHealthy')
            
            msg = ""
            
            # Check if the cell is healthy
            if is_healthy: msg += f'cell:{cell_id} is healthy. '
            else: msg += f'cell:{cell_id} is not healthy. '
            
            # Check if the Urls match
            for url in cell_urls:
                if url in cell_endpoints:
                    msg += f'cell URL: {url} is correct. '
                else:
                    msg += f'cell URL: {url} is incorrect. '


            return (msg)

    except Exception as e:
         # Ignore ConditionalCheckFailedException but raise other exceptions
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise
