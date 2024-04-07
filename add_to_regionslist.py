# Use this table can add all serviced region to dynamodb
import boto3

dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
table_name='cloudping_regions'
table = dynamodb.Table(table_name)
region = "us-east-2"

ec2 = boto3.client("ec2", region_name=region)
ec2_responses = ec2.describe_regions()
ssm_client = boto3.client('ssm', region_name=region)
for resp in ec2_responses['Regions']:
    region_id = resp['RegionName']
    tmp = '/aws/service/global-infrastructure/regions/%s/longName' % region_id
    ssm_response = ssm_client.get_parameter(Name = tmp)
    region_name = ssm_response['Parameter']['Value'] 
    
    
    Items_value = int(ec2_responses['Regions'].index(resp))+1
    region_value = region_id
    region_name = region_name
    active = "active_value"
    # print ("Item", Items_value,"region_id:",region_id,"region_name:",region_name)

    item = {
    'Items': Items_value,
    'region': region_value,
    'region_name': region_name,
    'active':active,
    'active_from':"True",
    "active_to":"True"
    }
    
    response = table.put_item(Item=item)






