import boto3

def lambda_handler(event, context):

        dynamodb = boto3.client('dynamodb')
        
        dynamodb.put_item(TableName='tbl_router', Item= {'marketId':{'S':'europe'},'cellId':{'S':'cell-0001'},'currentCapacity':{'N':'2'},
            'endPoint_1':{'S':'https://xxxx.execute-api.eu-north-1.amazonaws.com/'},
            'endPoint_2':{'S':'https://yyyy.execute-api.eu-west-1.amazonaws.com/'},
            'isHealthy':{'BOOL':True},'maxCapacity':{'S':'10'},'regionCode_1':{'S':'eu-north-1'},
            'regionCode_2':{'S':'eu-west-1'},
            'userIds': {'SS':[
                'test@email.com',
                'test2@email.com'
                ]}
        })
        
        dynamodb.put_item(TableName='tbl_router', Item= {'marketId':{'S':'europe'},'cellId':{'S':'cell-0002'},'currentCapacity':{'N':'2'},
            'endPoint_1':{'S':'https://aaaaa.execute-api.eu-north-1.amazonaws.com/'},
            'endPoint_2':{'S':'https://bbbbb.execute-api.eu-west-1.amazonaws.com/'},
            'isHealthy':{'BOOL':True},'maxCapacity':{'S':'10'},'regionCode_1':{'S':'eu-north-1'},
            'regionCode_2':{'S':'eu-central-1'},
            'userIds': {'SS':[
                'test3@email.com',
                'test4@email.com'
                ]}
        })
