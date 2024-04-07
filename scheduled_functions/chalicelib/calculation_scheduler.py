import boto3
import json
import base64


def get_curr_region():
    my_session = boto3.session.Session()
    my_region = my_session.region_name
    return my_region

def schedule(event, calc_func_name):
    session = boto3.Session()
    dynamodb = session.resource('dynamodb', region_name=get_curr_region())
    regions_table = dynamodb.Table('cloudping_regions')
    stored_avgs_table = dynamodb.Table('cloudping_stored_avgs')
    lambda_client = session.client('lambda', region_name=get_curr_region())

    timeframes_to_store = ['1D', '1W', '1M', '1Y']

    regions_response = regions_table.scan()
    
    # regions_response = {'Items': [{'Items': '7', "region_name": "Us East (Ohio)", "active": "active_value", "region": "us-east-2"}]}

    for region in regions_response['Items']:
        region_id = region['region']
        # region_name = region['region_name']
        region_name = region['region']

        region_active = region['active']

        if region_active:
            for timeframe in timeframes_to_store:
                print(region_id, region_name, region_active, timeframe)
                # Invoke Lambda function
                lambda_response = lambda_client.invoke(
                    FunctionName=calc_func_name,
                    InvocationType='RequestResponse',
                    LogType='Tail',
                    Payload=json.dumps({
                        "region":region_id,
                        "execution_source": "scheduled",
                        "latency_range": timeframe
                    })
                )
                if lambda_response['StatusCode'] != 200:
                    print(lambda_response['FunctionError'], lambda_response['StatusCode'])
                    sys.exit(1)
                
           
                
                calculated_averages =base64.b64decode(lambda_response['LogResult']).decode('utf-8')
                json_start = calculated_averages.find('{')
                json_end = calculated_averages.rfind('}') + 1
                calculated_averages = calculated_averages[json_start:json_end]    
                
                # 將 JSON 字符串轉換為 Python 對象
                calculated_averages = json.loads(calculated_averages)               
                            
                # Store data received back in DynamoDB

                for avg in calculated_averages[region_id]:
                    region_to = avg['region_to']
                    avg_latency = avg['avg_latency']
                    
                    item = {
                        "index": "{}_{}_{}".format(region_id, region_to, timeframe),
                        "region_from": region_id,
                        "timeframe": timeframe,
                        "region_to": region_to,
                        "latency": avg_latency,
                        "p_10": avg['p_10'],
                        "p_25": avg['p_25'],
                        "p_50": avg['p_50'],
                        "p_75": avg['p_75'],
                        "p_90": avg['p_90'],
                        "p_98": avg['p_98'],
                        "p_99": avg['p_99']
                    }
                    
                    try:
                        response = stored_avgs_table.put_item(
                            Item=item
                        )
                    except:
                        print("An error occurred with the following item:")
                        print(item)
                        print(response)

    return {
        "message": "Function execution completed successfully.",
        "event": event
    }
