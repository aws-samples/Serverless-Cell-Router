import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

 
def lambda_handler(event, context):

    emailId = event.get('email')
    response, cellId = assign_cells_to_user(emailId)

    return {
        'statusCode': 200,
        'cellId': cellId,
        'body': json.dumps(response)
    }


def assign_cells_to_user(email_id): 
    try:
        table_name = 'tbl_router'
        sort_key = 'cellId'
        gsi_name = 'marketId-currentCapacity-index'
        
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
            return (f'cellId : {cell_id} , endPoint_1 : {end_point_1} , endPoint_2 : {end_point_2}', cell_id)
            

        # if the user is new then first find the cell with the minimum number of users. Global secondary index is used for optimizing search
        response = table.query(
            ProjectionExpression='cellId,currentCapacity,endPoint_1,endPoint_2',
            IndexName = gsi_name,
            KeyConditionExpression= Key('marketId').eq('europe'),
            ScanIndexForward=True,
            Limit=1
            )
            
        if 'Items' in response and len(response['Items']) > 0:
            record = response['Items'][0]
            cell_min = record.get(sort_key)
            current_cap = record.get('currentCapacity')
            end_point_1= record.get('endPoint_1')
            end_point_2= record.get('endPoint_2')
            
            # assign cell to the new user
            table.update_item( 
                Key={
                    'marketId':'europe',
                    'cellId':cell_min
                    },
                    UpdateExpression="ADD userIds :ui SET currentCapacity = :cc",
                    ExpressionAttributeValues={':ui': {email_id}, ':cc': current_cap + 1}
                    )
                
            return (f'cellID : {cell_min} , endPoint_1 : {end_point_1} , endPoint_2 : {end_point_2}', cell_min)

        else:
            return ('no cells found')
            

    except Exception as e:
        # Ignore ConditionalCheckFailedException but raise other exceptions
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise
