# last edition: 2024/02/11
# Introduction
* This project is for testing the AWS backbond speed. The project is refer from cloudping.co. There are some new regions deplyed after the original one made. There are some update in these four year. For example, the python3.7 are not available now. I used python3 3.10 in this project.


There are three major items in this project: 
1. ping-from-region  : This lambda function would ping each available region's dynamodb endpoint. And use deploy.sh deploy the lambda function to all regions.
The result would store in DynamoDB-PingTest

2. scheduled_function:The function would calcuate the ping result from every regions. The function would only in Ohin(default) Region.

3. frontend          : The frontned folder is the Flask package. The result's row and columne comes from cloudping_regions and the data would come from cloudping_stored_avgs.

There are three dynamoDB table are used in this project:
|DynamoDB|Partition Key|Sort Key|Global 1|Global 2|
|---|---|---|---|---|
|cloudping_regions|Item(N)|active(S)|active_from(String)|active_to(String)|
||||active_from-region-index|activ_to-region-index|
|cloudping_stored_avgs|Index(S)|||
|PingTest|region(S)|timestamp(S)||

* the cloudping_regions should add two addtional index with "Partition key":active_from(String) "Index name":active_from-region-index and "Partition key":active_to(String) "Index name":active_to-region-index


# Before Start
1. Install python venv

```
python -m venv tutorial-env
source tutorial-env/bin/acitve 
``` 

2. Apply AWS account Access keys

3. Install AWS CLI 

4. using ```aws configure``` and input the applyed Access Keys ```AWS Access Key ID```, ```AWS Secret Access Key```. Set```Default region name```as "us-east-2" and ```Default output format```as json.


# ping_from_region
1. change the itmes form deploy.sh - add "$" in the REGIONS and in the form loop change from ```REGIONS``` to ```$REGIONS```

2. add itmes in ./.chalice/config.json - ```  "lambda_memory_size":256,
  "lambda_timeout":600 ```
3. change the file ./.chalice/policy-dev.json ```Resource``` region and accountID as you want.

4. the app.py ```@app.schedule``` can set the frequency for hte cronjab

5. using ```chalice deploy``` deploy the function in the region that set in ```aws configure```. Check the DynamoDB table PingTest would get the result. Using deploy.sh if the function works. 

# scheduled_function
1. the app.py can set ```@app.schedule```

2. calculate_avgs.py - Doesn't change anything

3. calculation_scheduler.py - 
(1)```lambda_response``` has to change LogType as 'Tail'
(2)change ```calculated_averages =json.loads(lambda_response['Payload'].read().decode("utf-8"))```to 
```
                calculated_averages =base64.b64decode(lambda_response['LogResult']).decode('utf-8')
                json_start = calculated_averages.find('{')
                json_end = calculated_averages.rfind('}') + 1
                calculated_averages = calculated_averages[json_start:json_end]
```
(3) Use ```chalice deploy`` deploy application

# frontend
The forntend is using FLASK.

You should change the credentials as you want to use

## gunicorn and nginx
In the EC2 using venv and install gunicorn
```sudo amazon-linux-extras install nginx```
The setting for nginx can be referr following:
****

**/etc/nginx/conf.d/cloudping.conf**
```
# vim /etc/nginx/conf.d/cloudping.conf
[root@ip-172-31-26-22 conf.d]# cat cloudping.conf
server{
        location / {
                proxy_pass http://localhost:8080;
                proxy_redirect off;
                proxy_set_header Host $host:80;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }





}
```

Deploy

```
gunicorn -w 1 -b localhost:8080 main:app
```

## Docker



# Edit record:
1. First edition

# To do list:
1. Test for requirement of the deploy
