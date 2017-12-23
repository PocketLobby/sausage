import pandas as pd
from utilities.db import DB
from utilities.bill_helper import BillHelper
from vote_tallies.leg_vote_match import LegVoteMatch


class ConsVoteTally():
    """Calculates a vote tally for a specific constituent"""


    # I'm certain that we did _not_ send tally emails for the 2017-11-12 campaign
    LAST_KNOWN_TRANSACTION_EMAIL_SEND = "2017-11-11"

    constituent_id = None
    conn = DB()

    def __init__(self, constituent_id):
        self.constituent_id = constituent_id

    def get_cons_last_notification(self):
        """find the last time we notified the constituent"""

        records = self.conn.fetch_records("""
            SELECT MAX(sent_dttm)
            FROM transactional_emails
            WHERE to_user_id = %s
            """, (self.constituent_id,))
        dttm = records[0]
        return dttm[0] or self.LAST_KNOWN_TRANSACTION_EMAIL_SEND

    def get_bills_updated_since_last_notification(self):
        """Find all bills that have been updated since the last time we sent a vote tally"""

        cons_last_noti = self.get_cons_last_notification()
        results = self.conn.fetch_records("""
            SELECT DISTINCT(bill_id) as bill_id
            FROM bills
            WHERE house_activity_dttm > %s
                OR senate_activity_dttm > %s""",
            (cons_last_noti, cons_last_noti))

        return [result[0] for result in results]

    def vote_matches_for_bills(self):
        """Returns a pandas data frame of all votes we've collected for
        constituents and all legislators' matches"""

        # NOTE: this might be golfing, but the above queries could be
        # written as CTEs in the below query. All this class really cares
        # about is getting the vote matches for the constituent. This is
        # set up to make three queries where one would be fine.

        vote_matches = self.conn.fetch_records("""
        SELECT
          vcrvm.*
          , initcap(r.type) || '. ' || r.first_name || ' ' || r.last_name AS leg
        FROM vw_cons_reps_vote_matches AS vcrvm
          JOIN representatives AS r on r.bioguide_id = vcrvm.bioguide_id

        WHERE bill_id IN %(bills)s
          AND vcrvm.cons_vote IS NOT NULL
          AND vcrvm.constituent_id = %(constituent_id)s
          AND vcrvm.bioguide_id IN (
            SELECT bioguide_id
            FROM vw_cons_reps
            WHERE id = %(constituent_id)s
          )
        """, {"bills": tuple(self.get_bills_updated_since_last_notification()),
              "constituent_id": self.constituent_id,
        })

        return [LegVoteMatch(vm) for vm in vote_matches]

    def map_matches_to_df(self):
        vote_matches = self.vote_matches_for_bills()

        if not vote_matches:
            return pd.DataFrame()

        vote_matches_df = pd.DataFrame([v.__dict__ for v in vote_matches])

        # produces a summary with numerical values
        leg_matches = vote_matches_df.pivot_table(columns='leg',
                                                  index="bill_id",
                                                  values="agreement_int")

        # cons votes:
        cons_votes = vote_matches_df[['bill_id', 'cons_vote']]. \
            drop_duplicates(). \
            set_index('bill_id')

        # format the df
        cons_legs_vote_matches_df = cons_votes.join(leg_matches)
        cons_legs_vote_matches_df.rename(columns={"cons_vote": "Your vote"}, inplace=True)
        cons_legs_vote_matches_df['Your vote'] = cons_legs_vote_matches_df['Your vote'].apply(lambda x: x.capitalize())

        # replace numerical values with words
        cons_legs_vote_matches_df.replace({101: "Abstain",
                                           102: "No vote",
                                           100: "Match",
                                           -100: "No match",
                                           }, inplace=True)

        return cons_legs_vote_matches_df

    #notest
    def matches_to_html(self):
        """dataframe to html"""
        df = self.map_matches_to_df()
        if df.empty:
            return None

        df.index = [
            "<a href='" + BillHelper.linkify_bill(idx) + "'>" +
            BillHelper.convert_bill_name(idx) + "</a>"
            for idx in df.index
        ]

        formatted_table = BillHelper.convert_html_table_to_email_style(
            df.to_html(escape=False)
        )
        return formatted_table
