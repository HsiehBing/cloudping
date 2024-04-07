docker build .
docker tag cloudping:latest 369432261332.dkr.ecr.us-east-2.amazonaws.com/cloudping:latest
docker push 369432261332.dkr.ecr.us-east-2.amazonaws.com/cloudping
