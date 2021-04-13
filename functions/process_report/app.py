import datetime
import boto3

iam_client = boto3.client('iam')
s3_client = boto3.client('s3')


def cmd_success(response):
    metadata = response['ResponseMetadata']
    return True if metadata['HTTPStatusCode'] == 200 else False


def print_http_metadata(response):
    print(response['ResponseMetadata'])


def lambda_handler(event, context):

    response = ({'state': 'failed', 'errorCode': None, **event['report']})
    response['get_pass_count'] += 1  # increment pass count

    try:
        print('Pass count' + str(response['get_pass_count']))
        iam_response = iam_client.get_credential_report()
        if cmd_success(iam_response):
            dt = iam_response['GeneratedTime']
            date_key = datetime.datetime.strftime(dt, '%Y-%m-%d')
            time_key = datetime.datetime.strftime(dt, '%H%M%S')
            report_filename = '{}/report_{}.csv'.format(date_key, time_key)
            bucket_name = event['report']['bucket_name']  # Initialized in Init Var State
            s3_response = s3_client.put_object(Body=iam_response['Content'], Bucket=bucket_name, Key=report_filename)
            if cmd_success(s3_response):
                response['state'] = 'success'
            else:
                print_http_metadata(s3_response)
        else:
            print_http_metadata(iam_response)
    except (iam_client.exceptions.CredentialReportNotReadyException,
            iam_client.exceptions.CredentialReportNotPresentException,
            iam_client.exceptions.CredentialReportExpiredException) as err:
        response['errorCode'] = err.response['Error']['Code']

    return response
