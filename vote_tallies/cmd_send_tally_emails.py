import time
from utilities.db import DB
from vote_tallies.cons_vote_tally import ConsVoteTally
from vote_tallies.tally_mail import TallyMail
from utilities.configurator import Configurator

class CmdSendTallyEmails:
    """
    Send emails to constituents based on their voting behavior
    """

    config = Configurator().config
    TEST_EMAIL_RECIPIENT = config["test_transactional_email_address_to"]
    cmd_line_args = None
    constituent_tuple = ()


    def __init__(self, constituent_tuple, cmd_line_args):
        self.cmd_line_args = cmd_line_args
        self.constituent_tuple = constituent_tuple

    def execute(self):
        """Execute cli command"""

        cvt = self._cvt()
        bills = cvt.get_bills_updated_since_last_notification()

        to_address = self.constituent_tuple[1] if not self.cmd_line_args.test else self.TEST_EMAIL_RECIPIENT

        if bills and self.cmd_line_args.email:
            to = {
                "email" : to_address,
                "id"    : self.constituent_tuple[0],
                "first_name" : self.constituent_tuple[2],
            }

            self._send_email(to, cvt.matches_to_html())

    def _cvt(self):
        # NOTE: I want to be able to put this in the execute() method
        # but I'm having some real problems with the mocking library.
        # I'll pretend this in the service of isolating dependencies

        return ConsVoteTally(self.constituent_tuple[0])

    def _send_email(self, to, email_content):
        mailer = TallyMail(to, email_content, email_content, test=self.cmd_line_args.test)
        print(mailer.send())


    @classmethod
    def send_tally_emails(cls, args, klass=None):
        """
        Fetch all constituents and send tally emails after a vote

        Expects to be called from the accompanying send_tally_email_for_user.py
        script. Check there for the defined arguments.

        Optional klass kwarg can be passed in.
        """

        conn = DB()
        klass = klass if klass else CmdSendTallyEmails

        #query = "SELECT * FROM constituents LIMIT 2 OFFSET 4"
        query = "SELECT * FROM constituents"
        constituents = conn.fetch_records(query)

        for cons in constituents:
            print("processing %s" % cons[1])
            klass(cons, args).execute()
            # NOTE: I'm getting a connection refused error. Rate limit this shiz
            time.sleep(5.00)
