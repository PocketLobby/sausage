import unittest
import datetime
from unittest.mock import MagicMock

from vote_tally import ConsVoteTally

class ConsVoteTallyTest(unittest.TestCase):

    def setUp(self):
        self.arbitrary_dttm = datetime.datetime(2017, 11, 21, 18, 21, 51, 687954)
    def test_init(self):
        "sets required instance methods"
        cvt = ConsVoteTally(123)
        self.assertEqual(cvt.constituent_id, 123)

    def test_get_cons_last_notification(self):
        # When no previous records have been written
        cvt = ConsVoteTally(123)
        mocked_dttm = [(None,)]
        cvt.fetch_records = MagicMock(return_value=mocked_dttm)

        self.assertEqual(cvt.get_cons_last_notification(), "1900-01-01")

        # When at least one record exists
        cvt = ConsVoteTally(123)
        cvt.fetch_records = MagicMock(return_value=[(self.arbitrary_dttm,)])

        self.assertEqual(cvt.get_cons_last_notification(), self.arbitrary_dttm)

    def test_get_bills_updated_since_last_notification(self):
        # when at least one bill have been updated since
        mocked_bills = [('hr123-115',)]
        cvt = ConsVoteTally(123)
        cvt.get_cons_last_notification = MagicMock(return_value=(self.arbitrary_dttm,))
        cvt.fetch_records = MagicMock(return_value=mocked_bills)

        self.assertEqual(cvt.get_bills_updated_since_last_notification(),
                        [bills[0] for bills in mocked_bills])

        # when no bills have been updated since
        mocked_bills = []
        cvt = ConsVoteTally(123)
        cvt.get_cons_last_notification = MagicMock(return_value=(self.arbitrary_dttm,))
        cvt.fetch_records = MagicMock(return_value=mocked_bills)

        self.assertEqual(cvt.get_bills_updated_since_last_notification(), [])
