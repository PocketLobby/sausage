import unittest
import datetime
from unittest.mock import MagicMock

from vote_tallies.cons_vote_tally import ConsVoteTally

class ConsVoteTallyTest(unittest.TestCase):

    def setUp(self):
        self.arbitrary_dttm = datetime.datetime(2017, 11, 21, 18, 21, 51, 687954)
        self.default_constituent_id = 1
        self.default_cvt = self.make_cvt()

    def make_cvt(self):
        return ConsVoteTally(123)

    def test_golden_path_init(self):
        "sets required instance methods"
        cvt = self.default_cvt
        self.assertEqual(cvt.constituent_id, 123)

    def test_get_cons_last_notification(self):
        # When no previous records have been written
        cvt = self.default_cvt
        mocked_dttm = [(None,)]
        cvt.conn.fetch_records = MagicMock(return_value=mocked_dttm)

        self.assertEqual(cvt.LAST_KNOWN_TRANSACTION_EMAIL_SEND,
                         cvt.get_cons_last_notification())

        # When at least one record exists
        cvt = self.make_cvt()
        cvt.conn.fetch_records = MagicMock(return_value=[(self.arbitrary_dttm,)])

        self.assertEqual(self.arbitrary_dttm, cvt.get_cons_last_notification())

    def test_get_bills_updated_since_last_notification(self):
        # when at least one bill have been updated since
        mocked_bills = [('hr123-115',)]
        cvt = self.make_cvt()
        cvt.get_cons_last_notification = MagicMock(return_value=(self.arbitrary_dttm,))
        cvt.conn.fetch_records = MagicMock(return_value=mocked_bills)

        self.assertEqual([bills[0] for bills in mocked_bills],
                         cvt.get_bills_updated_since_last_notification())

        # when no bills have been updated since
        mocked_bills = []
        cvt = self.make_cvt()
        cvt.get_cons_last_notification = MagicMock(return_value=(self.arbitrary_dttm,))
        cvt.conn.fetch_records = MagicMock(return_value=mocked_bills)

        self.assertEqual([], cvt.get_bills_updated_since_last_notification())

    def db_return_list(self):
        """Represents a list of tuples that would come back from a DB query"""
        return [
            (8, 'M000133', 'hr1-115', None, 'against', None, None, 'Sen. Edward Markey'),
            (8, 'M000312', 'hr1-115', None, 'against', None, None, 'Rep. James McGovern'),
            (8, 'W000817', 'hr1-115', None, 'against', None, None, 'Sen. Elizabeth Warren'),
            (8, 'M000133', 'hr1207-115', None, 'for', None, None, 'Sen. Edward Markey'),
            (8, 'M000312', 'hr1207-115', 'for', 'for', False, True, 'Rep. James McGovern'),
            (8, 'W000817', 'hr1207-115', None, 'for', None, None, 'Sen. Elizabeth Warren'),
            (8, 'M000133', 's807-115', 'for', 'for', False, True, 'Sen. Edward Markey'),
            (8, 'M000312', 's807-115', None, 'for', None, None, 'Rep. James McGovern'),
            (8, 'W000817', 's807-115', 'for', 'for', False, True, 'Sen. Elizabeth Warren'),
            (8, 'M000133', 'sres333-115', 'for', 'abstain', True, False, 'Sen. Edward Markey'),
            (8, 'M000312', 'sres333-115', None, 'abstain', True, None, 'Rep. James McGovern'),
            (8, 'W000817', 'sres333-115', 'for', 'abstain', True, False, 'Sen. Elizabeth Warren')
        ]

    def test_map_matches_to_df(self):
        cvt = self.make_cvt()
        cvt.conn.fetch_records = MagicMock(return_value=self.db_return_list())

        ret = cvt.map_matches_to_df()
        correct_df_columns = ["Your vote",
                              "Rep. James McGovern",
                              "Sen. Edward Markey",
                              "Sen. Elizabeth Warren"]

        self.assertListEqual(correct_df_columns, ret.columns.tolist())

        uniq_bills_cnt = len(set([row[2] for row in self.db_return_list()]))
        self.assertEqual(uniq_bills_cnt, len(ret))

    def test_map_matched_to_df_with_no_recent_votes(self):
        cvt = self.make_cvt()
        cvt.vote_matches_for_bills = MagicMock(return_value=[])

        ret = cvt.map_matches_to_df()
        self.assertIsNone(ret)


    def test_vote_matches_for_bills(self):
        cvt = self.make_cvt()

        cvt.conn.fetch_records = MagicMock(return_value=self.db_return_list())
        just_bills = [bill[2] for bill in self.db_return_list()]
        cvt.get_bills_updated_since_last_notification = MagicMock(return_value=just_bills)

        matches = cvt.vote_matches_for_bills()
        i = 0
        for match in matches[0:2]:
            self.assertEqual(self.db_return_list()[i][0], match.constituent_id)
            i += 1
