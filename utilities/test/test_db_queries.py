"""
There are SQL queries being referenced all over the code and the tests are mocking the trip to the database. This
set of tests should be used to guarantee that the queries being made are returning the expected results
"""

import unittest

import yaml

from utilities.db import DB


class DBQueryTest(unittest.TestCase, DB):

    def setUp(self):
        self.table_name = 'transactional_emails'
        self.table_fixture = self.load_table_fixture()
        self.truncate_table()
        self.insert_transactional_emails()

    def load_table_fixture(self):
        with open("utilities/sql.yml") as yml:
            data_map = yaml.safe_load(yml)
            return data_map['tables'][self.table_name]

    def truncate_table(self):
        stmt = "TRUNCATE %s" % self.table_name
        self.execute(stmt)

    def transactional_email_tuples(self):
        fixture_hashes = self.table_fixture['test_fixtures']

        return [tuple(record.values()) for record in fixture_hashes]

    def insert_transactional_emails(self):
        # TODO: bulk insert will be faster
        for record in self.transactional_email_tuples():
            self.execute("""INSERT INTO transactional_emails (email_type, to_user_id, to_email, sent_dttm)
                         VALUES (%s, %s, %s, %s)""", record)

    def execute_query(self, query_name, params=None):
        return self.fetch_records(self.table_fixture[query_name]['sql'], params)

    def test_last_constituent_notification_query_returns_latest_date(self):
        user_id_tup = (123,)

        all_fixtures = self.fetch_records("SELECT sent_dttm FROM transactional_emails WHERE to_user_id = %s", user_id_tup)
        dates = [record[0] for record in all_fixtures]
        most_recent = sorted(dates)[-1]

        result = self.execute_query('last_constituent_notification', user_id_tup)
        result = result[0][0] # First column in first row

        self.assertEqual(most_recent, result)