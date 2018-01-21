import pandas as pd

from utilities.bill_helper import BillHelper
from utilities.db import DB
from vote_tallies.leg_vote_match import LegVoteMatch


class ConsVoteTally(DB):
    """Calculates a vote tally for a specific constituent"""


    # I'm certain that we did _not_ send tally emails for the 2017-11-12 campaign
    LAST_KNOWN_TRANSACTION_EMAIL_SEND = "2017-11-11"

    constituent_id = None

    def __init__(self, constituent_id):
        self.constituent_id = constituent_id

    def get_cons_last_notification(self):
        """find the last time we notified the constituent"""

        records = self.fetch_records("""
            SELECT MAX(sent_dttm)
            FROM transactional_emails
            WHERE to_user_id = %s
            """, (self.constituent_id,))
        dttm = records[0]
        return dttm[0] or self.LAST_KNOWN_TRANSACTION_EMAIL_SEND

    def vote_matches_for_bills(self):
        """Returns a pandas data frame of all votes we've collected for
        constituents and all legislators' matches"""

        vote_matches = self.fetch_records("""
            SELECT
              vcrvm.*
              , initcap(r.type) || '. ' || r.first_name || ' ' || r.last_name AS leg
            FROM vw_cons_reps_vote_matches AS vcrvm
              JOIN representatives AS r on r.bioguide_id = vcrvm.bioguide_id

            WHERE bill_id IN %(bills)s
              -- This is where congress has voted but the constituent has not
              AND vcrvm.cons_vote IS NOT NULL
              AND vcrvm.constituent_id = %(constituent_id)s
              AND vcrvm.bioguide_id IN (
                SELECT bioguide_id
                FROM vw_cons_reps
                WHERE id = %(constituent_id)s
          )
        """, {"bills": tuple(self.bill_ids_updated_since_last_notification()),
              "constituent_id": self.constituent_id,
        })

        return [LegVoteMatch(vm) for vm in vote_matches]

    def bill_ids_updated_since_last_notification(self):
        """
        Returns a set of bill ids relevant for sending tally emails


        Looks for a bill that a constituent has voted since his/her last tally
        email. Additionally, if a bill has been updated by either legislative
        chamber && the bill has been voted on by the constituent, show that too.
        """

        bill_ids = self.fetch_records("""
            SELECT
              DISTINCT(bill_id) as bill_id
            FROM bills
            -- TODO: solve for NULL
            WHERE GREATEST(house_activity_dttm, senate_activity_dttm)::DATE > %(last_contact_date)s
              -- Don't bother consituent with bills that congress has voted
              -- but the user abstained.
              AND bill_id NOT IN (
                SELECT
                  DISTINCT(b.bill_id)
                FROM user_votes AS uv
                  JOIN bills as b ON b.id = uv.bill_id
                WHERE uv.vote = 'abstain'
                  AND uv.constituent_id = %(constituent_id)s
              )

            UNION

            SELECT
              DISTINCT( b.bill_id ) as bill_id
            FROM user_votes AS uv
              JOIN bills as b on b.id = uv.bill_id
            WHERE uv.constituent_id = %(constituent_id)s
              AND uv.vote_collected_dttm::DATE > %(last_contact_date)s
              
            """, {'constituent_id': self.constituent_id,
                  'last_contact_date': self.get_cons_last_notification()})

        return [bill_id[0] for bill_id in bill_ids]

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
