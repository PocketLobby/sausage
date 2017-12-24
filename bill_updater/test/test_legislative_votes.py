import unittest
import json
from unittest.mock import MagicMock

from bill_updater.legislative_votes import LegislativeVotes

class LegislativeVotesTest(unittest.TestCase):

    example_data_aye_vote_count = 263
    example_data_nay_vote_count = 145
    example_data_present_vote_count = 0
    example_data_abstain_vote_count = 21
    example_data_total_vote_count = (example_data_aye_vote_count +
                                     example_data_nay_vote_count +
                                     example_data_abstain_vote_count +
                                     example_data_present_vote_count)

    def example_data(self):
        data_file = open('bill_updater/test/vote_123.json', 'r')
        return json.load(data_file, encoding='UTF-8')


    def example_insert_tuple(self):
        """NOTE: this is a fairly brittle test conditioned on the data returned
        from the fixture vote_123.json"""

        return ('hr',
                'h',
                '2017',
                '2017-03-02T10:43:00-05:00',
                self.example_data_total_vote_count,
                0.5,
                'Agreed to',
                115,
                'http://clerk.house.gov/evs/2017/roll123.xml',
                '2017-12-23T17:09:24-05:00',
                'h123-115.2017',
                self.example_data_aye_vote_count,
                self.example_data_nay_vote_count,
                self.example_data_abstain_vote_count,
                self.example_data_present_vote_count)


    def basic_obj(self):
        lv = LegislativeVotes('h123-116.2018')
        lv._injest_json_data_for_vote = MagicMock(return_value=self.example_data())
        return lv

    @property
    def lv(self):
        return self.basic_obj()

    def test_init(self):
        self.assertEqual('h123', self.lv.vote_id)
        self.assertEqual('2018', self.lv.congress_year)
        self.assertEqual('116', self.lv.congress)

    def test_passage_requirement(self):
        self.assertEqual(self.lv.passage_requirement, 0.5)

    def test_insert_tuple(self):
        self.assertEqual(self.example_insert_tuple(), self.lv.insert_tuple)

    def test_yay_voter_cnt(self):
        # Sometimes, "yes" votes are registered as "Aye"
        self.assertEqual(self.example_data_aye_vote_count, self.lv.yay_voter_cnt)

        # Sometimes, "yes" votes are registered as "Yea"
        lv = LegislativeVotes('h123-116.2018')
        alt_yes = self.example_data()
        alt_yes["votes"]["Yea"] = alt_yes['votes'].pop('Aye')
        lv._injest_json_data_for_vote = MagicMock(return_value=alt_yes)

        self.assertEqual(self.example_data_aye_vote_count, lv.yay_voter_cnt)

    def test_nay_voter_cnt(self):
        # Sometimes, "no" votes are registered as "No"
        self.assertEqual(self.example_data_nay_vote_count, self.lv.nay_voter_cnt)

        # Sometimes, "no" votes are registered as "Nay"
        lv = LegislativeVotes('h123-116.2018')
        alt_no = self.example_data()
        alt_no["votes"]["Nay"] = alt_no['votes'].pop("No")
        lv._injest_json_data_for_vote = MagicMock(return_value=alt_no)

        self.assertEqual(self.example_data_nay_vote_count, lv.nay_voter_cnt)

    def test_present_voter_cnt(self):
        self.assertEqual(self.example_data_present_vote_count,
                         self.lv.present_voter_cnt)

    def test_upsert_into_bill_votes(self):
        # fake a db
        db = MagicMock()
        db.execute = MagicMock(return_value=True)

        lv = self.basic_obj()

        lv.db_cur = db
        lv.upsert_bill_votes()
        lv.db_cur().execute.assert_called_once_with(unittest.mock.ANY,
                                                    lv.insert_tuple)
