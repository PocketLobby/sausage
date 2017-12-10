"""The canonical source for bills that we're tracking"""
import json
from utilities.configurator import Configurator
from utilities.db import DB
from utilities.bill_helper import BillHelper

class TrackedBill(DB):

    config = Configurator().config
    congress_data_fs_root = config['congress_data_fs_root']

    def __init__(self, bill_id):
        self.cur = self.conn.cursor()
        self.bill_id = bill_id

    def get_bill_details(self):
        "returns a dict with the details of the bill in hr123-115 format"

        full_path = BillHelper.bill_fs_location(self.bill_id)

        with open(full_path) as json_data:
            data = json.load(json_data)

        return data

    def upsert_tuple(self):
        "Create a tuple suitable for upserting in a database"

        data = self.get_bill_details()


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
    def upsert_bill_id(self):
        "Update the bill's details in the database"
        upsert_tup = self.upsert_tuple(self.bill_id)
        return self.upsert(upsert_tup)

    # notest
    def upsert(self, upsert_tuple = None):
        "Given a tuple suitable for upserting, send it to the database"
        upsert_tuple = upsert_tuple if upsert_tuple else self.upsert_tuple()
        self.db_cur().execute("""
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
                    house_vote_style = self._map_how(hsh.get("how", None))

                    if house_vote_style == "rc":
                        house_vote_id = self._get_roll_call(hsh)

                if hsh.get("where", False) == "s":
                    senate_vote_style = self._map_how(hsh.get("how", None))

                    if senate_vote_style == "rc":
                        senate_vote_id = self._get_roll_call(hsh)

        return (house_vote_style
                , house_vote_id
                , senate_vote_style
                , senate_vote_id)

    def _get_roll_call(self, action_hash):
        return action_hash.get("where", "") + action_hash.get("roll", "") + "-115.2017"

    def _map_how(self, how):
        if "voice" in how.lower():
            return "vv"
        if "roll" in how:
            return "rc"
        if "unanimous consent" in how.lower():
            return "uc"
        return None

    #notest
    @classmethod
    def update_all_pl_bills(cls):
        db = DB()
        # FIXME: take away the LIMIT 1
        db.db_cur().execute("""SELECT DISTINCT(bill_id) FROM bills LIMIT 1""")
        bills = [bills[0] for bills in db.db_cur().fetchall()]

        for bill in bills:
            TrackedBills(bill).upsert
