# 最後編輯時間：2024/04/07
# 說明：
* 該專案是基於cloudping.co對於AWS各Region之間的Latency測試並統計，然而Cloudping在四年前完成後並無持續更新，例如目前部分package不適用python3.7以及Lambda使用。在本專案中將用python3.10進行部署

## 服務說明
1. ping-from-region：本專案中透過```describe ec2```查詢在該account中可以ping的region，並透過lambda ping各個dynamodb的節點以獲得region間的latency，並將結果存至PingTest的DynamoDb之中。

2. scheduled_function：在先前的ping-from-region取得的raw data會在此進行統計，並將資料存至cloudping_stored_avgs的DynamoDb中。

3. frontend：該部分是透過FLASK的方式部署網頁，並輸入Access keys以取得對DynamoDB的存取權限

## DynamoDB 配置
* DynamoDB的Table配置可以參考下表：

|DynamoDB|Partition Key|Sort Key|Global 1|Global 2|
|---|---|---|---|---|
|cloudping_regions|Items(N)|active(S)|active_from(String)|active_to(String)|
||||active_from-region-index|active_to-region-index|
|cloudping_stored_avgs|Index(S)|||
|PingTest|region(S)|timestamp(S)||

需要特別注意的是在cloudping_region中會需要額外設定Global tables

## 配置上傳

在Cloudping的上傳中是透過chalice上傳，相關說明可以查看AWS chalice github說明
https://github.com/aws/chalice

主要會用到的部署
```
# 進行部署
chalice deploy
# 刪除部署
chalice delete
```

# 設計細節

## 開始前設定
1. Python venv安裝

```
python3.10 -m venv tutorial-env
source tutorial-env/bin/acitve 
```
參考資料：https://docs.python.org/zh-tw/3/tutorial/venv.html
相關package安裝請參考requirements.txt

2.申請AWS account Access key 

3.安裝AWS CLI

4. 開啟Terminal並輸入 ```aws configure``` 並輸入先前設定的 Access ID以及Key ```AWS Access Key ID```, ```AWS Secret Access Key```. 另外將```Default region name```設定為 "us-east-2" 以及 ```Default output format```設為 ```json```

5. 在us-east-2的DynamoDB建立tables

|DynamoDB|Partition Key|Sort Key|Global 1|Global 2|
|---|---|---|---|---|
|cloudping_regions|Items(N)|active(S)|active_from(String)|active_to(String)|
||||active_from-region-index|active_to-region-index|
|cloudping_stored_avgs|Index(S)|||
|PingTest|region(S)|timestamp(S)||

* 建立完後執行add_to_regionslist.py將region的資訊加至cloudping_regions的DynamoDB tables中

## ping_from_region
在ping_from_region資料夾內有：
(1)app.py
(2)deploy.sh
(3).chalice

1. app.py
該部分設定與cloudping相同，唯一可以注意的是在初期部署測試時可以透過```@app.schedule```這個function修改cronjob頻率

2. deploy.sh
該部分主要是透過shell將Lambda部署到各個Region中，這部分主要需要將```REGIONS=```後增加```$```，以及在for迴圈中將```REGIONS```改為```$REGIONS```

3. .chalice
此資料夾中會有兩個檔案
(1)config.json: 這個設定主要是lambda function的設定，會需要調整的是lambda memory 以及timeout
(2)policy-dev.json：這個policy是lambda在使用時的policy需要將```Resource```改為需要設定的Region以及accountID

## scheduled_function
該資料夾內有：
(1) app.py
(2) deploy.sh
(3) .chalice
(4) chalicelib

1. app.py
這部分與ping_from_region有些不同，透透貨call function的方式將chalicelib中的function呼叫進行使用，這邊也有設定cronjob，這邊的cronjob會在ping完各個region後22分鐘開始計算。

2. deploy.sh
目前僅以```chalice deploy```進行部署，並不會使用該shell。該lambda僅會部署在單一region

3. .chalice
(1) config.json的設定為lambda layer的設定，支援的lambda layer可以參考
https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html
(2) policy-dev.json 為該lambda的policy設定，需要注意的是需要將Resource改為正確的accountID

1. chalicelib
(1) calculate_avgs.py
該部分主要是將計算結果的float改為int

(2) calculation_scheduler.py
* 在Lambda中的LogType需改為Tail
* 將原先的calculated_averages改為以下內容
```
calculated_averages =base64.b64decode(lambda_response['LogResult']).decode('utf-8')
json_start = calculated_averages.find('{')
json_end = calculated_averages.rfind('}') + 1
calculated_averages = calculated_averages[json_start:json_end]    
calculated_averages = json.loads(calculated_averages)
```

## frontend
主要部署是透過app中的main.py透過FLASK建立網頁，需要在credentials設定相關權限
credentials可以參考以下設定：
```
[default]
aws_access_key_id = 
aws_secret_access_key = 
region = us-east-2
output = json
```

# 部署
## 一、AWS CLI設定

.aws/config 建議用以下設置：
```
region = us-east-2
output = json
```
 
## 二、python venv 以及package安裝
1. 建立venv
```
python3.10 -m venv tutorial-env
```
2. 啟用venv
```
source tutorial-env/bin/activate
```
3. 安裝package
```
pip3 install -r requirements. txt
```

## 三、DynamoDB建立
1. 照以下列表建立

|DynamoDB|Partition Key|Sort Key|Global 1|Global 2|
|---|---|---|---|---|
|cloudping_regions|Items(N)|active(S)|active_from(String)|active_to(String)|
|active_from-region-index|active_to-region-index(S)||||
|cloudping_stored_avgs|Index(S)|||
|PingTest|region(S)|timestamp(S)||

2. 執行add_to_regionslist.py
```python3 add_to_regionslist.py```


## 四、ping_from_region部署
1. ```cd ./ping_from_region```
2. 修改 ./ping_from_region/.chalice/policy-dev.json，將Resource改為正確的accountID
3. 在嘗試部署階段可以先以cd至資料夾ping_from_region使用```chalice deploy```先部署在Ohio並查看是否有正確，確定無誤後可以執行```sh deploy.sh```

## 五、scheduled_functions部署
1. ```cd ./scheduled_functions```
1. 修改 ./scheduled_functions/.chalice/config.json中的AccountID
2. 修改 ./scheduled_functions/.chalice/policy-dev.json中的AccountID
3. ```chalice deploy```


## 五、frontend設定

## gunicorn 及 nginx 安裝
在EC2中使用venv並安裝nginx

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

# 編輯記錄
* 2024/04/07 編輯README_zh.md

# 待做事項
1. 在ping_from_region中deploy.sh若執行時會透過chalice部署，然而chalice deploy在建立時會建立IAM role，當使用shell在所以regions中部署Lambda時雖然會跳錯但是仍會持續部署Lambda，不過在刪除時會因為沒有IAM role可以刪除因而跳錯中斷，該部分尚未解決。

2. 在scheduled_functions.chalicelib中calculate_avgs看能不能改回float






