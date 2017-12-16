class LegVoteMatch():
    """
    A plain ol' python object to facilitate vote matches


    Reads in records returned from vw_cons_reps_vote_match_records and converts
    them to objects that can be manipulated for various reasons
    """

    CONSITUENT_ABSTENTION_INT = 101
    LEGISLATOR_NOT_VOTED_INT = 102
    CONS_LEG_MATCH_INT = 100
    CONS_LEG_NOT_MATCH_INT = -100

    def __init__(self, vw_cons_reps_vote_match_record):
        (self.constituent_id,
         self.bioguide_id,
         self.bill_id,
         self.leg_vote,
         self.cons_vote,
         self.either_abstain_bool,
         self.cons_leg_vote_match_bool,
         self.leg,
         ) = vw_cons_reps_vote_match_record
        self.agreement_int = self.map_match_to_int()

    def map_match_to_int(self):
        """
        Map a numeric representation of vote match given a (leg vote, constituent vote) tuple



        The business rules are:
            1. If the constituent abstains, return immediately
            2. If the legislator has not voted, return immediately
            3. Return a positive number for a match, a negative number for a miss
        """
        if self.cons_vote == 'abstain':
            return self.CONSITUENT_ABSTENTION_INT

        if not self.leg_vote:
            return self.LEGISLATOR_NOT_VOTED_INT #102

        if self.leg_vote == self.cons_vote:
            return self.CONS_LEG_MATCH_INT#100
        else:
            return self.CONS_LEG_NOT_MATCH_INT #-100
