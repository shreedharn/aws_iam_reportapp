import boto3
import botocore

iam_client = boto3.client('iam')
def lambda_handler(event, context):
    response = {'state': 'failed'}
    try:
        cmd_response = iam_client.get_credential_report()
        response['state'] = 'success'
        response['format'] = cmd_response['ReportFormat']
    except botocore.exceptions.ClientError as err: 
        print(err)

    return response