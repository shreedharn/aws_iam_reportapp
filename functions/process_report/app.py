import datetime
import boto3
import botocore

iam_client = boto3.client('iam')
s3_client = boto3.client('s3')


def cmd_success(response):
    metadata = response['ResponseMetadata']
    return True if metadata['HTTPStatusCode'] == 200 else False


def print_http_metadata(response):
    print(response['ResponseMetadata'])


def lambda_handler(event, context):
    response = {'state': 'failed'}
    try:
        iam_response = iam_client.get_credential_report()
        if cmd_success(iam_response):
            response_header = iam_response['ResponseMetadata']['HTTPHeaders']
            datetime_str = response_header['date']
            dt = datetime.datetime.strptime(datetime_str, '%a, %d %b %Y %H:%M:%S %Z')
            date_key = datetime.datetime.strftime(dt, '%Y-%m-%d')
            time_key = datetime.datetime.strftime(dt, '%H%M%S')
            report_filename = '{}/report_{}.csv'.format(date_key, time_key)
            bucket_name = event['report']['bucket_name'] # Initialized in Init Var State
            s3_response = s3_client.put_object(Body=iam_response['Content'], Bucket=bucket_name, Key=report_filename)
            if cmd_success(s3_response):
                response['state'] = 'success'
            else:
                print_http_metadata(s3_response)
        else:
            print_http_metadata(iam_response)
    except botocore.exceptions.ClientError as err:
        print(err)

    return response
