import csv
import datetime
import os

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
KEY_1 = {'active': 'access_key_1_active', 'last_rotated': 'access_key_1_last_rotated',
         'last_used': 'access_key_1_last_used_date', 'key_flag': 'access_key_1_flag'}
KEY_2 = {'active': 'access_key_2_active', 'last_rotated': 'access_key_2_last_rotated',
         'last_used': 'access_key_2_last_used_date', 'key_flag': 'access_key_2_flag'}


class ReportValidator:

    def __init__(self, max_age=45, validation_time=datetime.datetime.now(datetime.timezone.utc)):
        self.max_age = max_age
        self.now = validation_time

    def __get_delta(self, datetime_str):
        str_dt = datetime.datetime.strptime(datetime_str, DATE_TIME_FORMAT)
        str_dt = str_dt.replace(tzinfo=datetime.timezone.utc)
        return self.now - str_dt

    def __check_age(self, key, entry):
        access_key_issues = {}
        rotation_key_flag = usage_key_flag = False
        last_rotated = entry[key['last_rotated']]
        last_used = entry[key['last_used']]
        is_key_active = True if entry[key['active']] == 'true' else False

        if last_rotated != 'N/A':
            delta = self.__get_delta(last_rotated)
            if delta.days >= self.max_age:
                rotation_key_flag = True  # key has not be rotated for Max age

        if last_used != 'N/A':
            delta = self.__get_delta(last_used)
            if delta.days < self.max_age:
                usage_key_flag = True  # key is used recently within Max age time limit

        if rotation_key_flag:
            if is_key_active:  # key is still active --> flag
                access_key_issues[key['last_rotated']] = 'flagged'
            if usage_key_flag:  # an aged key is used sometime in the recent past --> flag
                access_key_issues[key['last_used']] = 'flagged'

        return access_key_issues

    def validate_entry(self, entry):
        entry_status = {}
        if entry['mfa_active'] == 'false':
            entry_status['mfa_status'] = 'flagged'
        key_1_issues = self.__check_age(KEY_1, entry)
        key_2_issues = self.__check_age(KEY_2, entry)
        return {**entry_status, **key_1_issues, **key_2_issues}

    def validate_report(self, filename):
        validation_issues = {}
        print(f'Validating file {filename} filesize: {os.path.getsize(filename):5d}')
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                issues = self.validate_entry(row)
                if len(issues) > 0:
                    validation_issues[row['user']] = issues
        return validation_issues



