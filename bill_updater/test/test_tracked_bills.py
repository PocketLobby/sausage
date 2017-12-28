import unittest

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

        for known_bill in ["s504-115", "hr2519-115", "hjres111-115"]:
            tb = TrackedBill(known_bill)
            bill_dict = tb.get_bill_details()

            self.assertEqual(type(bill_dict), dict)
            self.assertEqual(bill_dict['bill_id'], known_bill)

    def test_upsert_tuple(self):
        tb = TrackedBill(self.known_bill)

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

