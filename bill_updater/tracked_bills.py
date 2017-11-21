"""The canonical source for bills that we're tracking"""
import psycopg2
import json

class DB:
    """Holds a connection to the database"""
    # TODO: put these into env vars
    conn = psycopg2.connect(host='psql02.thedevranch.net',
        user='brycemcd',
        database='pocketlobby_dev')

class TrackedBills(DB):

    congress_data_fs_root = "/media/brycemcd/bkp/congress/congress/data/"

    def __init__(self):
        self.cur = self.conn.cursor()
        self.cur.execute("""SELECT DISTINCT(bill_id) FROM bills""")
        self.bills = [bills[0] for bills in self.cur.fetchall()]

    def get_bill_details(self, bill_id):
        "returns a dict with the details of the bill in hr123-115 format"

        full_path = self._fs_path_to_bill(bill_id)

        with open(full_path) as json_data:
            data = json.load(json_data)
        return data

    def upsert_tuple(self, bill_id):
        "Create a tuple suitable for upserting in a database"

        data = self.get_bill_details(bill_id)


        house_vote_style , \
        house_vote_id, \
        senate_vote_style, \
        senate_vote_id = self._vote_styles_and_id(data)

        upsert_tuple = (
                data["bill_id"]
                , data["history"]["active"]
                , data["history"].get("house_passage_result", None) == 'pass'
                , data["history"].get("house_passage_result_at", None)
                , data["history"].get("senate_passage_result", None) == 'pass'
                , data["history"].get("senate_passage_result_at", None)
                , house_vote_style
                , house_vote_id
                , senate_vote_style
                , senate_vote_id
                )
        return upsert_tuple

    #notest
    def upsert_bill_id(self, bill_id):
        "Given a bill_id, update the bills details in the database"
        upsert_tup = self.upsert_tuple(bill_id)
        return self.upsert(upsert_tup)

    # notest
    def upsert(self, upsert_tuple):
        "Given a tuple suitable for upserting, send it to the database"
        self.cur.execute("""
            INSERT INTO bills (
                bill_id
                , active
                , passed_house_bool
                , house_activity_dttm
                , passed_senate_bool
                , senate_activity_dttm
                , house_passage_type
                , most_recent_house_vote_id
                , senate_passage_type
                , most_recent_senate_vote_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (bill_id) DO UPDATE SET
            (   active
                , passed_house_bool
                , house_activity_dttm
                , passed_senate_bool
                , senate_activity_dttm
                , house_passage_type
                , most_recent_house_vote_id
                , senate_passage_type
                , most_recent_senate_vote_id
            ) =
            (
                EXCLUDED.active
                , EXCLUDED.passed_house_bool
                , EXCLUDED.house_activity_dttm
                , EXCLUDED.passed_senate_bool
                , EXCLUDED.senate_activity_dttm
                , EXCLUDED.house_passage_type
                , EXCLUDED.most_recent_house_vote_id
                , EXCLUDED.senate_passage_type
                , EXCLUDED.most_recent_senate_vote_id
            )
        """, upsert_tuple)

        return self.conn.commit()

    def _vote_styles_and_id(self, data):
        "Given a list of actions, return a tuple of (house_vote_style, house_vote_id, senate_vote_style, senate_vote_id"
        house_vote_style = None
        house_vote_id = None
        senate_vote_style = None
        senate_vote_id = None

        for hsh in sorted(data["actions"], key=lambda hsh: hsh["acted_at"]):
            if hsh.get("type", False) == "vote":

                if hsh.get("where", False) == "h":
                    house_vote_style = self.map_how(hsh.get("how", None))

                    if house_vote_style == "rc":
                        house_vote_id = self._get_roll_call(hsh)

                if hsh.get("where", False) == "s":
                    senate_vote_style = self.map_how(hsh.get("how", None))

                    if senate_vote_style == "rc":
                        senate_vote_id = self._get_roll_call(hsh)

        return (house_vote_style
                , house_vote_id
                , senate_vote_style
                , senate_vote_id)

    def _get_roll_call(self, action_hash):
        return action_hash.get("where", "") + action_hash.get("roll", "") + "-115.2017"

    def map_how(self, how):
        if "voice" in how.lower():
            return "vv"
        if "roll" in how:
            return "rc"
        if "unanimous consent" in how.lower():
            return "uc"
        return None

    def _fs_path_to_bill(self, bill_id):
        house, bill, congress = self._deconstruct_bill_id(bill_id)

        full_path = ""
        full_path += self.congress_data_fs_root + "/"
        full_path += congress + "/bills/"
        full_path += house + "/" + bill + "/data.json"
        return full_path

    def _deconstruct_bill_id(self, bill_id):
        splits = bill_id.split("-")

        congress = splits[1]
        bill = splits[0]

        if "hr" in bill_id:
            house = "hr"
        elif "hjres" in bill_id:
            house = "hjres"
        elif "s" in bill_id:
            house = "s"

        return (house, bill, congress)
