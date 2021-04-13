# IAM Report App with AWS Step Functions

The application uses AWS Step Functions to get IAM Credential report and upload it to a specified S3 bucket. Application also
generates the report in case if it is not available.

## Prerequisites
S3 bucket where the report has to be uploaded. Bucket name has to be passed during SAM deploy

`sam deploy --parameter-overrides BucketName=your_bucketname`

## Report App States
![State flow](https://github.com/shreedharn/aws_iam_reportapp/blob/master/report_states.png)

Refer Report App [states language file](https://github.com/shreedharn/aws_iam_reportapp/blob/master/statemachine/report_app.asl.json)