import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):

    emailId = event.get('email')
    response = assign_cells_to_user(emailId)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def assign_cells_to_user(email_id): 
    try:
        table_name = 'tbl_router'
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # check if user already has assigned cell
        response = table.query(
            ProjectionExpression='cellId,endPoint_1,endPoint_2',
            KeyConditionExpression= Key('marketId').eq('europe'),
            FilterExpression=Attr('userIds').contains(email_id)
            )
            
        if 'Items' in response and len(response['Items']) > 0:
            record= response['Items'][0]
            cell_id= record.get('cellId')
            end_point_1= record.get('endPoint_1')
            end_point_2= record.get('endPoint_2')
            return (f'cellId : {cell_id} , endPoint_1 : {end_point_1} , endPoint_2 : {end_point_2}')
        
        else:
            return ('no cells for the user found')
            

    except Exception as e:
        # Ignore ConditionalCheckFailedException but raise other exceptions
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise
