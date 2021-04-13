import boto3
import botocore

iam_client = boto3.client('iam')


def lambda_handler(event, context):
    # initial state to failed and s3 bucket passed in the Init Var State
    response = {'state': 'failed', **event['report']}
    try:

        cmd_response = iam_client.generate_credential_report()
        response['state'] = cmd_response['State']
    except botocore.exceptions.ClientError as err:
        print(err)

    return response
