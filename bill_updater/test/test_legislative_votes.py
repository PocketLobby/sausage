import json
import unittest
from unittest.mock import MagicMock

from bill_updater.legislative_votes import LegislativeVotes, IndividualLegislatorVote


class LegislativeVotesTest(unittest.TestCase):

    example_data_aye_vote_count = 263
    example_data_nay_vote_count = 145
    example_data_present_vote_count = 0
    example_data_abstain_vote_count = 21
    example_data_total_vote_count = (example_data_aye_vote_count +
                                     example_data_nay_vote_count +
                                     example_data_abstain_vote_count +
                                     example_data_present_vote_count)

    @staticmethod
    def example_data():
        data_file = open('bill_updater/test/vote_123.json', 'r')
        json_data = json.load(data_file, encoding='UTF-8')
        data_file.close()
        return json_data

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
        self.assertEqual('h123', self.lv.vote_id_path)
        self.assertEqual('2018', self.lv.congress_year)
        self.assertEqual('116', self.lv.congress)

    def test_raw_data(self):
        lv = self.lv
        lv._injest_json_data_for_vote = MagicMock(return_value=self.example_data())
        self.assertEqual(lv.raw_data, self.example_data())

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

    def test_abstain_voter_cnt(self):
        self.assertEqual(self.example_data_abstain_vote_count,
                         self.lv.abstain_voter_cnt)

    def test_upsert_into_bill_votes(self):
        # fake a db
        db = MagicMock()
        db.execute = MagicMock(return_value=True)

        lv = self.basic_obj()

        lv.db_cur = db
        lv.upsert_bill_votes()
        lv.db_cur().execute.assert_called_once_with(unittest.mock.ANY,
                                                    lv.insert_tuple)


class IndividualLegislatorVoteTest(unittest.TestCase):

    list_of_map_tuples = [
        ("S123", "B000944"),
        ("S234", "B000123"),
        ("S345", "B000446"),
    ]

    vote_tuples = [
        ('h123-116.2018', 'B000123', 'for'),
        ('h123-116.2018', 'C000123', 'against'),
        ('h123-116.2018', 'E000123', 'present'),
        ('h123-116.2018', 'G000123', 'abstain'),
    ]

    pretend_bill_id = 'h123-116.2018'

    @property
    def yay_voter_ids(self):
        """pretend bioguide_ids of legislators that voted for a bill"""

        return ['B000123', 'A000123']

    @property
    def nay_voter_ids(self):
        """pretend bioguide_ids of legislators that voted against a bill"""

        return ['C000123', 'D000123']

    @property
    def present_voter_ids(self):
        """pretend bioguide_ids of legislators that were present for a vote"""

        return ['E000123', 'F000123']

    @property
    def abstain_voter_ids(self):
        """pretend bioguide_ids of legislators that abstained from a vote"""

        return ['G000123', 'H000123']

    def test_map_is_a_dict(self):
        lv = IndividualLegislatorVote('h123-116.2018')
        lv._fetch_map_from_db = MagicMock(return_value=self.list_of_map_tuples)
        keys = [tup[0] for tup in self.list_of_map_tuples]
        self.assertListEqual(keys, list(lv.bioguide_lis_map.keys()))

    def test_lis_id_to_bioguide_id(self):
        lv = IndividualLegislatorVote('h123-116.2018')
        lv._fetch_map_from_db = MagicMock(return_value=self.list_of_map_tuples)

        self.assertEqual("B000944", lv.lis_to_bioguide_id("S123"))

    def test_convert_person_to_bioguide(self):

        lv = IndividualLegislatorVote('h123-116.2018')
        lv._fetch_map_from_db = MagicMock(return_value=self.list_of_map_tuples)

        # need to convert lis_id to bioguide_id
        self.assertEqual("B000944", lv.convert_to_bioguide_id("S123"))

        # no need to convert
        self.assertEqual("B000944", lv.convert_to_bioguide_id("B000944"))

        # invalid and not converted
        self.assertIsNone(lv.convert_to_bioguide_id("AZ123"))

    def test_votes_dict(self):
        # NOTE: This is probably just testing that mocks work ... it's probably
        # still useful to bring attention to this test if the API of
        # this class changes.

        lv = IndividualLegislatorVote('h123-116.2018')

        lv._yay_voters = MagicMock(return_value=self.yay_voter_ids)
        lv._nay_voters = MagicMock(return_value=self.nay_voter_ids)
        lv._present_voters = MagicMock(return_value=self.present_voter_ids)
        lv._abstain_voters = MagicMock(return_value=self.abstain_voter_ids)

        # NOTE: for, against, present and abstain are all "magic words" in the
        # Pocket Lobby domain language. These signify a consistent language for
        # votes across all bill types and houses https://xkcd.com/927/

        self.assertListEqual(self.yay_voter_ids, lv.votes_dict["for"])
        self.assertListEqual(self.nay_voter_ids, lv.votes_dict["against"])
        self.assertListEqual(self.present_voter_ids, lv.votes_dict["present"])
        self.assertListEqual(self.abstain_voter_ids, lv.votes_dict["abstain"])

    def test_vote_types_to_insert_tuples(self):
        lv = IndividualLegislatorVote('h123-116.2018')

        lv._yay_voters = MagicMock(return_value=self.yay_voter_ids)
        lv._nay_voters = MagicMock(return_value=self.nay_voter_ids)
        lv._present_voters = MagicMock(return_value=self.present_voter_ids)
        lv._abstain_voters = MagicMock(return_value=self.abstain_voter_ids)

        all_voter_cnt = len(self.yay_voter_ids) + \
            len(self.nay_voter_ids) + \
            len(self.present_voter_ids) + \
            len(self.abstain_voter_ids)

        votes = lv.vote_types_to_insert_tuples()

        self.assertEqual(all_voter_cnt, len(votes))
        self.assertIn(('h123-116.2018', 'B000123', 'for'), votes)
        self.assertIn(('h123-116.2018', 'C000123', 'against'), votes)
        self.assertIn(('h123-116.2018', 'E000123', 'present'), votes)
        self.assertIn(('h123-116.2018', 'G000123', 'abstain'), votes)

    def test_save_individual_vote(self):
        # fake a db
        db = MagicMock()
        db.execute = MagicMock(return_value=True)

        lv = IndividualLegislatorVote('h123-116.2018')
        lv.db_cur = db

        lv.vote_types_to_insert_tuples = MagicMock(return_value=self.vote_tuples)
        lv.db_cur().execute = MagicMock()

        lv.upsert_individual_vote(self.vote_tuples[0])
        lv.db_cur().execute.assert_called_once_with(unittest.mock.ANY,
                                                    self.vote_tuples[0])

    def test_upsert_all_votes(self):
        lv = IndividualLegislatorVote('h123-116.2018')

        lv.vote_types_to_insert_tuples = MagicMock(return_value=self.vote_tuples)
        lv.upsert_individual_vote = MagicMock(return_value=True)

        lv.upsert_all_votes()
        self.assertEqual(len(self.vote_tuples), lv.upsert_individual_vote.call_count)
        lv.upsert_individual_vote.assert_called_with(('h123-116.2018', 'G000123', 'abstain'))
