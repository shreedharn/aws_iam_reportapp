import os
import datetime
import json
import tempfile
import boto3
import reportvalidator as iam_rv


iam_client = boto3.client('iam')
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')


def cmd_success(response):
    metadata = response['ResponseMetadata']
    return True if metadata['HTTPStatusCode'] == 200 else False


def print_http_metadata(response):
    print(response['ResponseMetadata'])


def get_flagged_entries(report_content):
    with tempfile.TemporaryDirectory() as dir_name:
        try:
            with tempfile.NamedTemporaryFile(dir=dir_name, mode='wt', delete=False) as fp:
                fp.write(report_content.decode('UTF-8'))  # report is stored in a temporary file within a temp directory
                fp.close()
                temp_filename = fp.name
            flagged_entries = iam_rv.ReportValidator().validate_report(temp_filename)
            print(f'Report successfully generated with {len(flagged_entries):4d} entries')
        finally:
            os.unlink(temp_filename)  # Temporary directory will be cleaned up anyway
    return flagged_entries


def lambda_handler(event, context):
    response = ({'state': 'failed', 'errorCode': None, **event['report']})
    response['get_pass_count'] += 1  # increment pass count

    try:
        print(f'Pass count {response["get_pass_count"]:2d}')
        iam_response = iam_client.get_credential_report()
        if cmd_success(iam_response):
            dt = iam_response['GeneratedTime']
            date_key = datetime.datetime.strftime(dt, '%Y-%m-%d-%H-%M-%S').split('-')
            report_filename = 'year={}/month={}/day={}/hour={}/report.csv' \
                .format(date_key[0], date_key[1], date_key[2], date_key[3])  # Split by year, month, day, hour
            bucket_name = event['report']['bucket_name']  # Initialized in Init Var State
            report_content = iam_response['Content']
            s3_response = s3_client.put_object(Body=report_content, Bucket=bucket_name, Key=report_filename)
            if cmd_success(s3_response):
                response['state'] = 'success'
            else:
                print_http_metadata(s3_response)

            report_issues = get_flagged_entries(report_content)
            topic_arn = event['report']['notification_topic']  # Initialized in Init Var State
            message = json.dumps(report_issues, indent=4)
            sns_client.publish(TopicArn=topic_arn, Subject='IAM Validation report', Message=message)
        else:
            print_http_metadata(iam_response)
    except (iam_client.exceptions.CredentialReportNotReadyException,
            iam_client.exceptions.CredentialReportNotPresentException,
            iam_client.exceptions.CredentialReportExpiredException) as err:
        response['errorCode'] = err.response['Error']['Code']

    return response
