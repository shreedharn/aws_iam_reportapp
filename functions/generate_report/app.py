import boto3


iam_client = boto3.client('iam')


def lambda_handler(event, context):
    # initial state to failed
    response = {'state': 'failed', **event['report']}
    cmd_response = iam_client.generate_credential_report()
    response['state'] = cmd_response['State']



