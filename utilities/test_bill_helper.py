import unittest
import os

from bill_helper import BillHelper

class BillHelperTest(unittest.TestCase):

    def test_fs_linkify_bill(self):
        "convert a bill to its expected location on the filesystem"

        bill_types = [
            'hconres',
            'hjres',
            'hr',
            'hres',
            's',
            'sconres',
            'sjres',
            'sres',
        ]

        for kind in bill_types:
            bill = kind + "123-115"
            path = "/media/brycemcd/bkp/congress/congress/data/115/bills/%s/%s123/data.json" % (kind, kind)
            self.assertEqual(BillHelper.bill_fs_location(bill), path)
