import datetime
import unittest
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
        cvt = self.default_cvt
        self.assertEqual(cvt.constituent_id, 123)

    def test_get_cons_last_notification(self):
        # When no previous records have been written
        cvt = self.default_cvt
        mocked_dttm = [(None,)]
        cvt.fetch_records = MagicMock(return_value=mocked_dttm)

        self.assertEqual(cvt.LAST_KNOWN_TRANSACTION_EMAIL_SEND,
                         cvt.get_cons_last_notification())

        # When at least one record exists
        cvt = self.make_cvt()
        cvt.fetch_records = MagicMock(return_value=[(self.arbitrary_dttm,)])

        self.assertEqual(self.arbitrary_dttm, cvt.get_cons_last_notification())

    def test_get_bills_updated_since_last_notification(self):
        # when at least one bill have been updated since
        mocked_bills = [('hr123-115',)]
        cvt = self.make_cvt()
        cvt.get_cons_last_notification = MagicMock(return_value=(self.arbitrary_dttm,))
        cvt.fetch_records = MagicMock(return_value=mocked_bills)

        self.assertEqual([bills[0] for bills in mocked_bills],
                         cvt.bill_ids_updated_since_last_notification())

        # when no bills have been updated since
        mocked_bills = []
        cvt = self.make_cvt()
        cvt.get_cons_last_notification = MagicMock(return_value=(self.arbitrary_dttm,))
        cvt.fetch_records = MagicMock(return_value=mocked_bills)

        self.assertEqual([], cvt.bill_ids_updated_since_last_notification())

    @staticmethod
    def db_return_list():
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
        cvt.fetch_records = MagicMock(return_value=self.db_return_list())

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
        self.assertTrue(ret.empty)

    def test_vote_matches_for_bills(self):
        cvt = self.make_cvt()

        cvt.fetch_records = MagicMock(return_value=self.db_return_list())
        cvt.bill_ids_updated_since_last_notification = MagicMock(return_value=[])

        matches = cvt.vote_matches_for_bills()
        i = 0
        for match in matches[0:2]:
            self.assertEqual(self.db_return_list()[i][0], match.constituent_id)
            i += 1
        # make sure that the we capture both congressional updates and bills
        # voted by constituent iff the constituent has voted on the bill after
        # a vote

        cvt.bill_ids_updated_since_last_notification.assert_called_once()

    @property
    def results_of_bill_ids_updated_since_last_notification(self):
        return [('hr123', None), ('s234', None)]

    def test_bill_ids_updated_since_last_notification(self):

        # before the user has voted even once or they have not voted since the last notification we sent him/her
        cvt = self.make_cvt()
        cvt.fetch_records = MagicMock(return_value=[])
        cvt.get_cons_last_notification = MagicMock(return_value=cvt.LAST_KNOWN_TRANSACTION_EMAIL_SEND)

        self.assertEqual([], cvt.bill_ids_updated_since_last_notification())

        # when the user has voted since the last notification
        cvt = self.make_cvt()
        cvt.fetch_records = MagicMock(return_value=self.results_of_bill_ids_updated_since_last_notification)
        cvt.get_cons_last_notification = MagicMock(return_value=cvt.LAST_KNOWN_TRANSACTION_EMAIL_SEND)

        bill_ids = [bill[0] for bill in self.results_of_bill_ids_updated_since_last_notification]
        self.assertEqual(bill_ids, cvt.bill_ids_updated_since_last_notification())
