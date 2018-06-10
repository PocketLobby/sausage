from datetime import datetime as dt
from utilities.db import DB
from bill_updater.tracked_bill import TrackedBill

# Read results from queue
# Look up vote in bills to see if it's there. Add it if not.
# Store constituent vote
#


class ConstituentVoteConverter:
    """
    Some lower level methods to aid in the process of saving constituent votes
    """

    @staticmethod
    def timestamp_converter(unix_timestamp):
        """Converts a unix timestamp to iso8601
        :param unix_timestamp: Unix timestamp with microseconds
        """

        # NOTE: we _should_ have received a unix timestamp with microseconds.
        # In case we didn't, let's not tear our hair out trying to find this
        # bug later.
        if len(unix_timestamp) == 13:
            to_convert = int(unix_timestamp)/1000
        else:
            to_convert = int(unix_timestamp)

        converted = dt.utcfromtimestamp(to_convert)

        return converted.isoformat()

    @staticmethod
    def user_token_converter(user_token):
        """Converts a user token into a user_id

        :param user_token: a character hash representing a user to other systems
        """

        user_id, user_token = DB().fetch_one("""
            SELECT
                id
                , user_token
                FROM constituents
                WHERE user_token = %s
            """, (user_token, ))

        return user_id

    @staticmethod
    def bill_id_converter(bill_id_str, call_times=1, maximum_call_times=2):
        """converts a bill id like hr123 into the PK representation. Returns None if bill is not inserted"""


        bill_id_int = ConstituentVoteConverter._fetch_bill_record(bill_id_str)


        # NOTE: frequently, it will be the case where the bill has not been
        # inserted into the database. In that case, we want to insert the bill
        # into the database and then retry this operation.
        #
        # I don't like the mutation of bill_id_int nor that methods in this class
        # need to know how to insert bills into the database.
        #
        # If the insert fails, then this method will raise an exception by
        # design. I want to know when this is happening so I can understand why

        # NOTE: I'm the king of infinite loops
        if not bill_id_int and call_times <= maximum_call_times:
            ConstituentVoteConverter._add_bill(bill_id_str)
            return ConstituentVoteConverter.bill_id_converter(bill_id_str,
                                                              call_times=2)

        bill_id_int = bill_id_int[0]


        return bill_id_int

    @staticmethod
    def _fetch_bill_record(bill_id_str):
        return DB().fetch_one("""
            SELECT
                id
            FROM bills
            WHERE bill_id = %s
            """, (bill_id_str, ))


    @staticmethod
    def _add_bill(bill_id_str, bill_kreator_klass=TrackedBill):
        if "-" in bill_id_str:
            bill_id_str, _ = bill_id_str.split("-")

        bill = bill_kreator_klass(bill_id_str)
        bill.upsert()


class ConstituentVoteCreator:
    """
    Given that I have a user token, timestamp, bill_id and vote,
    I should store that as a user_vote in the database
    """

    def __init__(self, user_token, unix_timestamp, bill_id, vote, konverter_klass=ConstituentVoteConverter):
        """
        Inits the class and sets the instance variables

        :param user_token: NOT the user id. The unique token assigned to a user
        :param unix_timestamp: just what it says
        :param bill_id: a bill id with the session suffix i.e. hr123-115
        :param vote: one of for, against or abstain
        :param konverter_klass: a class that can be called for conversion of user_id, bill_id and dttm stuff
        """

        converters = konverter_klass
        valid_votes = ['for', 'against', 'abstain']
        self.constituent_id = converters.user_token_converter(user_token)
        self.dttm = converters.timestamp_converter(unix_timestamp)
        self.bill_id_int = converters.bill_id_converter(bill_id)

        if vote not in valid_votes:
            raise ValueError("A vote must be one of %s" % valid_votes)

        self.vote = vote

        self._db_conn = DB()

    def commit_user_vote(self):
        commit = self._db_conn.execute(
            """
            INSERT INTO user_votes
            (constituent_id, bill_id, vote, vote_collected_dttm)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (constituent_id, bill_id)
            DO UPDATE
                SET (vote, vote_collected_dttm) = 
                    (EXCLUDED.vote, EXCLUDED.vote_collected_dttm)
                WHERE user_votes.constituent_id = EXCLUDED.constituent_id
                AND user_votes.bill_id = EXCLUDED.bill_id
            """, (self.constituent_id, self.bill_id_int, self.vote, self.dttm)
        )
        return commit

