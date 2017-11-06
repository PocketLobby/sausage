import numpy as np

import psycopg2
import pandas as pd
import json
# import constituent_emails.tally as tally_mailer

class VoteTally():
    """Compares constituent votes to legislative votes

    NOTE: I originally created this as a Jupyter Notebook and am porting it
    to be a command line utility. Later versions could remove the pandas
    requirement as well as other things to make it much more efficient

    This class violates all sorts of good engineering practices. Needs a
    good refactor
    """

    # TODO: put these into env vars
    conn = psycopg2.connect(host='psql01.thedevranch.net',
        user='pl_reporting',
        database='pocketlobby')

    for_int = 1
    against_int = -1
    abstain_int = 0

    def __init__(self, bills):
        """Takes a list of bills and a user_token to create a vote tally obj

        bills (list) = an list of bills with a hyphen and congress i.e. hr123-115
        user_token (string) = a unique user token
        """
        self.bills = bills

    def rep_votesdf(self):
        """Returns a pandas data frame of all votes we've collected for
        legislators filtered on the bills passed in to init this object"""

        query = """
        SELECT
        *
        FROM vw_rep_vote_summaries
        WHERE bill_id IN %(bills)s
        """

        rep_votes = pd.read_sql(query,
                                self.conn,
                                params={"bills" : tuple(self.bills)})
        return rep_votes

    def rep_vote_score_table(self):
        """A table of legislators and their votes ready for elementwise comparison

        rows are bioguide_ids to uniquely identify a legislator
        columns are bills
        values are either 1, -1 or 0 to indicate they voted for, against or abstained
        """

        return self._convert_vote_to_score(self.rep_votesdf()). \
                pivot_table(index="bioguide_id",
                            columns="bill_id",
                            values="vote")

    def cons_votesdf(self):
        "Returns a pandas data frame of all votes we've collected for constituents"""

        query = """
        SELECT
        *
        FROM vw_cons_vote_summaries
        WHERE bill_id IN %(bills)s
        """

        con_votes = pd.read_sql(query,
                                self.conn,
                                params={"bills" : tuple(self.bills)})
        return con_votes

    def cons_vote_score_table(self):
        """A table of all consituents and their votes ready for elementwise comparison

        rows are user_tokens (unique)
        columns are bills
        values are either 1, -1 or 0 to indicate they voted for, against or abstained
        """
        return self._convert_vote_to_score(self.cons_votesdf()). \
                        pivot_table(index="user_token",
                                columns="bill_id",
                                values="vote")

    def cons_reps(self):
        """A table of all constituents and who represents them in congress"""
        query = """
        SELECT
        *
        FROM vw_cons_reps
        """

        return pd.read_sql(query, self.conn, params={"bills" : tuple(self.bills)})

    def _color_vote_word(self, val):
        color_map = {
                'No Match' : 'red',
                'No Vote'  : 'grey',
                'Match'    : 'green',
                }

        color = 'red' if val == 'No Match' else 'green'
        color = 'grey' if val == 'No Vote' else color
        return 'color: %s' % color_map.get(val, 'black')

    def _get_unique_user_tokens(self, df):
        return df['user_token'].unique()

    def _create_numerical_user_rep_match_df(self, user_score_mtrx, rep_score_mtrx, columns, indexes):
        """Does element wise multiplication to produce an `[n x m]` numerical
        matrix. Returns a data frame with rows = reps and columns = bills
        """
        numerical_match_mtrx = np.array(rep_score_mtrx) * np.array(user_score_mtrx)

        return pd.DataFrame(numerical_match_mtrx,
                            columns=columns,
                            index=indexes)

    def _rep_match_display(self, constituents_reps, rep_matchesdf):

        return constituents_reps. \
                    set_index('bioguide_id')[['full_name']]. \
                    join(rep_matchesdf). \
                    set_index("full_name") .\
                    replace({0  : " - ",
                             1  : "Match",
                             -1 : "No Match",
                             -2 : "No Vote",
                             2  : "No Vote",
                             None : "No Vote",
                            }). \
                    transpose()

    def _constituent_match_display(self, con_votes, user_token):
        cv = con_votes[ con_votes['user_token'] == user_token][['bill_id', 'vote']]

        cv = cv.set_index("bill_id")

        cv.columns = ['Your Vote']
        return cv

    def _produce_bill_match_table(self, constituent_votes, representative_votes):
        # NOTE: this used to produce very nice looking tables. Some ASCII
        # conversion error is being thrown
        return pd.concat([constituent_votes, representative_votes], axis=1). \
                    dropna()#. \
                    # style. \
                    # applymap(self._color_vote_word). \
                    # set_properties(**{'text-align' : 'center'})

    def create_html_comparison_table(self, user_token):
        rvst = self.rep_vote_score_table()
        rep_matchesdf = self._create_numerical_user_rep_match_df(self.cons_vote_score_table().loc[user_token],
                                                            rvst,
                                                            rvst.columns,
                                                            rvst.index
                                                           )

        cons_reps = self.cons_reps()
        con_votes = self.cons_votesdf()

        con_reps = cons_reps[ cons_reps['user_token'] == user_token ]
        con_reps['full_name'] = con_reps['type'] + " " + con_reps['rep_first_name'] + " " + con_reps['rep_last_name']
        rep_ids = con_reps['bioguide_id']
        print(rep_ids)

        rv = self._rep_match_display(con_reps, rep_matchesdf)
        cv = self._constituent_match_display(con_votes, user_token)

        return self._produce_bill_match_table(cv, rv).to_html()

    def _convert_vote_to_score(self, df):
        return df.replace({
            "for" : self.for_int,
            "against" : self.against_int,
            "abstain" : self.abstain_int,
            })
