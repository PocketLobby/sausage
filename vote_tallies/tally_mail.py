from sparkpost import SparkPost
from utilities.configurator import Configurator
from utilities.db import DB



class TallyMail():
    """
    Send an email to a constituent

    NOTE: this requires using a SparkPost account and including an API key
    in sausage_config.conf
    """
    testing_destination_email_addresses = ['bryce@bridgetownint.com',
                                           'thea.briggs@gmail.com']
    config = Configurator().config


    def __init__(self, to, html_table, test=False):
        """Create a new TallyMail instance

        params:

        to (string) = email address of recipient
        html_table (string) = HTML formatted table to include in template
        subject (string) = the subject of the message
        """

        self.spark_post = SparkPost(self.config['spark_post_api_key'])
        self.html_table = html_table

        self.to = to
        if test:
            self.to["email"] = "bryce@bridgetownint.com"
            self.to["id"] = -99


    def send(self):
        """Orchestraion of creating the message in email format, connecting to
        SMTP and sending the message"""

        response = self.spark_post.transmissions.send(
            recipients=[{
                "address": {
                    "email": self.to["email"],
                },
            }],
            template="tally-mail",
            use_draft_template=False,
            substitution_data={
                "name": self.to["first_name"],
                "bill_match_html": str(self.html_table),
            },
        )
        self.log_transaction()

        return response

    def log_transaction(self):
        db = DB()
        db.execute("""INSERT INTO transactional_emails
        (email_type, to_user_id, to_email, sent_dttm) VALUES
        (%s, %s, %s, NOW())""", ('tally_mail', self.to['id'], self.to['email']))

