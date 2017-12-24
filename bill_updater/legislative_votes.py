import json
from utilities.db import DB
from utilities.configurator import Configurator


class LegislativeVotes(DB):
    """
    Keep votes that happen in both houses updated in the db


    Expects vote_id in the form: h123-115.2017
    """

    vote_id = None
    congress = None
    congress_year = None

    def __init__(self, vote_id):
        self.vote_id, rest = vote_id.split("-")
        self.congress, self.congress_year = rest.split(".")

    # notest
    def _injest_json_data_for_vote(self):
        basepath = Configurator().config['congress_data_fs_root']

        with open(basepath + self.congress + "/votes/" + self.congress_year + "/" + self.vote_id + "/data.json") as json_data:
            return json.load(json_data, encoding='UTF-8')

    @property
    def raw_data(self):
        return self._injest_json_data_for_vote()

    @property
    def yay_voter_cnt(self):
        """Counts the number of legislators voting in favor"""

        return len(self._voter_id_list("Aye", "Yea"))

    @property
    def nay_voter_cnt(self):
        """Counts the number of legislators voting against"""

        return len(self._voter_id_list("No", "Nay"))

    @property
    def present_voter_cnt(self):
        """Counts the number of legislators present but not voting"""

        return len(self._voter_id_list("Present"))

    @property
    def abstain_voter_cnt(self):
        """Counts the number of legislators abstaining from voting"""

        return len(self._voter_id_list("Not Voting"))

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

    def _total_votes_cast(self):
        return (self.yay_voter_cnt +
                self.nay_voter_cnt +
                self.abstain_voter_cnt +
                self.present_voter_cnt)

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
