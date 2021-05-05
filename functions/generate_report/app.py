import boto3

iam_client = boto3.client('iam')


def cmd_success(response):  # generic helper function to be moved to separate layer
    metadata = response['ResponseMetadata']
    return True if metadata['HTTPStatusCode'] == 200 else False


def lambda_handler(event, context):
    # initialize state to failed
    response = {'state': 'failed', 'errorCode': None, **event['report']}
    response['get_pass_count'] += 1  # increment pass count
    print(f'Pass count {response["get_pass_count"]:2d}')
    iam_response = iam_client.generate_credential_report()
    if cmd_success(iam_response):
        print(f'IAM Response State: {iam_response["State"]}')
        if iam_response['State'] == 'COMPLETE':
            response['state'] = 'success'
        elif iam_response['State'] == 'STARTED' or iam_response['State'] == 'INPROGRESS':
            response['state'] = 'in progress'  # treat both status as In Progress
        else:
            print(f'Unexpected status {iam_response["State"]}!')  # unexpected response
    else:
        print(f'Generate Credential report failed {iam_response["State"]}')
    return response
