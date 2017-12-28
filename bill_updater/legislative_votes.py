import json
import re

from utilities.configurator import Configurator
from utilities.db import DB


class LegislativeVotes(DB):
    """
    Keep votes that happen in both houses updated in the db


    Expects vote_id in the form: h123-115.2017
    """

    vote_id = None
    congress = None
    congress_year = None

    def __init__(self, vote_id):
        self.vote_id = vote_id
        self.vote_id_path, rest = vote_id.split("-")
        self.congress, self.congress_year = rest.split(".")

    @property
    def raw_data(self):
        """The JSON that is returned from congress as a python dict"""

        return self._injest_json_data_for_vote()

    @property
    def yay_voter_cnt(self):
        """Counts the number of legislators voting in favor"""

        return len(self._yay_voters())

    @property
    def nay_voter_cnt(self):
        """Counts the number of legislators voting against"""

        return len(self._nay_voters())

    @property
    def present_voter_cnt(self):
        """Counts the number of legislators present but not voting"""

        return len(self._present_voters())

    @property
    def abstain_voter_cnt(self):
        """Counts the number of legislators abstaining from voting"""

        return len(self._abstain_voters())

    @property
    def passage_requirement(self):
        """Converts a fraction like 2/3 into a decimal"""

        divisor, dividend = self.raw_data["requires"].split("/")
        return (int(divisor) * 1.0) / (int(dividend) * 1.0)

    @property
    def insert_tuple(self):
        """Creates a tuple suitable for upserting into bill_votes"""

        return (self.raw_data.get('bill', {}).get("type"),
                self.raw_data.get('chamber'),
                self.raw_data.get('session'),
                self.raw_data.get('date'),
                self._total_votes_cast(),
                self.passage_requirement,
                self.raw_data.get('result'),
                self.raw_data.get('congress'),
                self.raw_data.get('source_url'),
                self.raw_data.get('updated_at'),
                self.raw_data.get('vote_id'),
                self.yay_voter_cnt,
                self.nay_voter_cnt,
                self.abstain_voter_cnt,
                self.present_voter_cnt
                )

    def upsert_bill_votes(self):
        """Insert a record _that there was a vote_ into the db"""

        self.db_cur().execute("""INSERT INTO bill_votes
            (
                bill_type
                , chamber
                , congressional_session
                , vote_dttm
                , vote_cnt
                , passage_requirement
                , result
                , congress
                , source_url
                , updated_dttm
                , vote_id
                , yea_vote_cnt
                , nay_vote_cnt
                , abstain_vote_cnt
                , present_vote_cnt
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (vote_id) DO NOTHING""", self.insert_tuple)
        return self.conn.commit()

    def _injest_json_data_for_vote(self):
        basepath = Configurator().config['congress_data_fs_root']

        with open(basepath + self.congress + "/votes/" + self.congress_year + "/" + self.vote_id_path + "/data.json") as json_data:
            return json.load(json_data, encoding='UTF-8')

    def _total_votes_cast(self):
        return (self.yay_voter_cnt +
                self.nay_voter_cnt +
                self.abstain_voter_cnt +
                self.present_voter_cnt)

    def _abstain_voters(self):

        return self._voter_id_list("Not Voting")

    def _present_voters(self):

        return self._voter_id_list("Present")

    def _nay_voters(self):

        return self._voter_id_list("No", "Nay")

    def _yay_voters(self):

        return self._voter_id_list("Aye", "Yea")

    def _voter_id_list(self, vote_key, alternative_key=None):
        """Return a list of legislator identifiers for a vote key


        A vote key is Aye, Yea, No, Nay, Present, Not Voting
        """

        votes = self.raw_data.get("votes", {})  # this is a dict

        if vote_key in votes.keys():
            vk = vote_key
        else:
            vk = alternative_key

        return [voter["id"] for voter in votes.get(vk)]

    # notest
    @classmethod
    def unpersisted_legislative_votes(cls):
        """Find all legislative votes that have not been saved and save them"""

        query = """
            SELECT DISTINCT most_recent_house_vote_id as vote_id
            FROM bills
            WHERE most_recent_house_vote_id IS NOT NULL

            UNION

            SELECT DISTINCT most_recent_senate_vote_id as vote_id
            FROM bills
            WHERE most_recent_senate_vote_id IS NOT NULL

            EXCEPT

            SELECT DISTINCT vote_id
            FROM bill_votes
        """

        bills = DB().fetch_records(query)
        for bill in bills:
            print(bill)


class IndividualLegislatorVote(LegislativeVotes):
    """Save individual legislator's votes to the database"""

    @property
    def bioguide_lis_map(self):
        """Creates a dictionary of lis_id : bioguide_id

        Helpful for converting between individuals on different vote types
        """
        return dict((k, v) for k, v in self._fetch_map_from_db())

    @property
    def votes_dict(self):
        """All voters mapped to the Pocket Lobby data domain language"""

        return {
            "for": self._yay_voters(),
            "against": self._nay_voters(),
            "present": self._present_voters(),
            "abstain": self._abstain_voters(),
        }

    def lis_to_bioguide_id(self, lis_id):
        """Convert a lis_id to a bioguide_id


        lis_ids are used for Senate votes while bioguide_ids are used for
        House votes. bioguide_id is unique per person

        NOTE: this should probably be refactored into a utility module
        or a representatives class
        """

        return self.bioguide_lis_map[lis_id]

    def convert_to_bioguide_id(self, person_id):
        """Convert a bioguide_id or a lis_ to a bioguide_id"""

        bioguide_id = None
        if len(person_id) is 7 and re.match(r"[A-Z]\d{6}", person_id):
            bioguide_id = person_id

        if len(person_id) is 4 and re.match(r"S\d{3}", person_id):
            bioguide_id = self.bioguide_lis_map[person_id]

        return bioguide_id

    def vote_types_to_insert_tuples(self):
        """Create an insert tuple for an individual legislator's vote

        person_id can be a bioguide_id or lis_id
        vote_id should take the form h123-115.2017
        vote should be one of the "magic four value: for, against, preent, abstain
        """

        votes = []
        for vote, voters in self.votes_dict.items():
            for person_id in voters:
                bioguide_id = self.convert_to_bioguide_id(person_id)
                votes.append((self.vote_id, bioguide_id, vote))

        return votes

    def upsert_all_votes(self):
        """For each vote parsed, insert it into the db"""

        for vote in self.vote_types_to_insert_tuples():
            self.upsert_individual_vote(vote)

    def upsert_individual_vote(self, vote_tuple):
        """Saves an individual vote to the database"""

        self.db_cur().execute("""
                INSERT INTO votes (vote_id, person_bioguide_id, vote)
                 VALUES(%s, %s, %s)
                 
                 ON CONFLICT (vote_id, person_bioguide_id) DO UPDATE
                 SET (vote) = (EXCLUDED.vote)
                 WHERE votes.vote_id = EXCLUDED.vote_id
                     AND votes.person_bioguide_id = EXCLUDED.person_bioguide_id
             """, vote_tuple)
        return self.conn.commit()

    def _fetch_map_from_db(self):
        return self.db_cur().fetchall("""
                SELECT lis_id, bioguide_id
                FROM representatives WHERE lis_id IS NOT NULL""")
