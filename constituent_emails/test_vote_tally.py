import unittest
import os
import pandas as pd
from bill_helper import BillHelper

class BillHelperTest(unittest.TestCase):

    def setUp(self):
        self.index = ['hr123', 's344-115', 'hr234', 'hjres111']
        self.df = pd.DataFrame({'Rep. Delta' : range(10),
                                'Sen. Beta' : range(10),
                                'Sen. Alpha' : range(10)})


    def test_linkify_bill(self):
        bill = 'hr123-115'
        self.assertEqual(BillHelper.linkify_bill(bill), "https://www.congress.gov/bill/115th-congress/house-bill/123/text")

        bill = 's123-115'
        self.assertEqual(BillHelper.linkify_bill(bill), "https://www.congress.gov/bill/115th-congress/senate-bill/123/text")

        bill = 'hjres123-115'
        self.assertEqual(BillHelper.linkify_bill(bill), "https://www.congress.gov/bill/115th-congress/house-joint-resolution/123/text")

    def test_index_sort(self):
        """Tests that hr123-115 is converted to H.R. 123"""

        idx = [BillHelper.convert_bill_name(idx) for idx in self.index]
        self.assertEqual(idx, ["H.R. 123", "S. 344", "H.R. 234", "H. J. Res. 111"])

    def test_df_column_sort(self):
        new_cols = BillHelper.sort_vote_match_columns(self.df.columns)
        self.assertListEqual(list(new_cols), ['Rep. Delta', 'Sen. Alpha', 'Sen. Beta'])
