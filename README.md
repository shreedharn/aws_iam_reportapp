# IAM Report App with AWS Step Functions

The application uses AWS Step Functions to generate IAM Credential report and upload to a specified S3 bucket.

## Prerequisites
S3 bucket where report has to be uploaded. Bucket name is passed during SAM deploy

`sam deploy --parameter-overrides BucketName=your_bucketname`

## Report App States
![State flow](https://github.com/shreedharn/aws_iam_reportapp/blob/master/report_states.png)

Refer Report App [states language file](https://github.com/shreedharn/aws_iam_reportapp/blob/master/statemachine/report_app.asl.json)