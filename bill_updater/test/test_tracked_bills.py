import unittest
import json
from unittest.mock import MagicMock, patch, mock_open

from bill_updater.tracked_bill import TrackedBill


class TrackedBillsTest(unittest.TestCase):

    def setUp(self):
        # this is brittle, it's known this bill is in the db
        self.known_bill = 's504-115'

    def test_init(self):
        "should return a list of bills. TODO: mock the call to the db"
        self.assertTrue(TrackedBill(self.known_bill).bill_id, self.known_bill)
        # self.assertTrue( self.known_bill in TrackedBills().bills )

    def test_get_bill_details(self):
        "should return dict of bill"


        tb = TrackedBill(self.known_bill)
        tb._bill_path = MagicMock(return_value="bill_updater/test/s504.json")

        bill_dict = tb.get_bill_details()

        self.assertEqual(type(bill_dict), dict)
        self.assertEqual(bill_dict['bill_id'], self.known_bill)

    def mock_bill_data(self):
        with open('bill_updater/test/s504.json') as json_data:
            data = json.load(json_data)
        return data

    def test_upsert_tuple(self):
        tb = TrackedBill(self.known_bill)
        tb.get_cur = MagicMock()
        tb.get_bill_details = MagicMock(return_value=self.mock_bill_data())

        right_answer = (self.known_bill
                , True
                , True
                , '2017-10-23T19:02:20-04:00'
                , True
                , '2017-09-26'
                , 'rc'
                , 'h570-115.2017'
                , 'uc'
                , None
                )
        self.assertEqual(tb.upsert_tuple(), right_answer)

