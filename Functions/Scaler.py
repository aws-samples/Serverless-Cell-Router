import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):

    cellId = event.get('cellId')
    awsAccountId = context.invoked_function_arn.split(":")[4]
    region = os.environ.get('AWS_REGION')
    response = evaluate_cell_capacity(cellId, awsAccountId, region)

    return {
        'statusCode': 200,
        'cellId': cellId,
        'body': json.dumps(response)
    }

def evaluate_cell_capacity(cell_id, aws_account_id, sqs_region): 
    try:
        
        table_name = 'tbl_router'
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        response = table.query(
            ProjectionExpression='cellId,currentCapacity,maxCapacity',
            KeyConditionExpression= Key('marketId').eq('europe') & Key('cellId').eq(cell_id)
            )
            
        if 'Items' in response and len(response['Items']) > 0:
            record= response['Items'][0]
            current_capacity= record.get('currentCapacity')
            max_capacity= record.get('maxCapacity')
            max_capacity_buffer = (70 * float(max_capacity)) / 100.0 # 70% of the max capacity has reached
            
             # if 70% of the max capacity has reached then send message to the simple queue service so
             # it can be picked up by the provision and deploy service
            if current_capacity >= max_capacity_buffer:
                msg = f'CellId: {cell_id} has reached max capacity with buffer: {max_capacity_buffer}'
                sqs = boto3.client('sqs')
                sqs.send_message(
                    QueueUrl = f'https://sqs.{sqs_region}.amazonaws.com/{aws_account_id}/CellProvisioning',
                    MessageBody = msg
                    )
                return ('notified')
            else:
                return ('capacity ok')
          
        else:
            return ('cell not found')
            

    except Exception as e:
         # Ignore ConditionalCheckFailedException but raise other exceptions
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise
                
