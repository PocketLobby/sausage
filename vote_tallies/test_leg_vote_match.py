import unittest

from vote_tallies.cons_vote_tally import LegVoteMatch

class LegVoteMatchTest(unittest.TestCase):

    def vote_agreement_row(self):
        return LegVoteMatch((8, 'M000312', 'hr1207-115', 'for', 'for', False, True, 'Rep. James McGovern'))

    def vote_disagreement_row(self):
        return LegVoteMatch((8, 'M000312', 'hr1207-115', 'for', 'against', False, True, 'Rep. James McGovern'))

    def cons_abstain_row(self):
        return LegVoteMatch((8, 'M000312', 'hr1207-115', 'for', 'abstain', False, True, 'Rep. James McGovern'))

    def leg_not_voted_row(self):
        return LegVoteMatch((8, 'M000312', 'hr1207-115', None, 'for', False, True, 'Rep. James McGovern'))

    def test_row_to_match_int(self):
        agree = self.vote_agreement_row()
        self.assertEqual(agree.CONS_LEG_MATCH_INT, agree.map_match_to_int())

        disagree = self.vote_disagreement_row()
        self.assertEqual(disagree.CONS_LEG_NOT_MATCH_INT, disagree.map_match_to_int())

        uabstain = self.cons_abstain_row()
        self.assertEqual(uabstain.CONSITUENT_ABSTENTION_INT, uabstain.map_match_to_int())

        leg_not_voted = self.leg_not_voted_row()
        self.assertEqual(leg_not_voted.LEGISLATOR_NOT_VOTED_INT, leg_not_voted.map_match_to_int())
