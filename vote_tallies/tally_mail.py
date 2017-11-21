import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class GenericMailer():
    """A class to set up a basic transactional email configuration"""

    email_from = "Pocket Lobby <email@pocketlobby.org>"

    def _connect_to_smtp(self):
        s = smtplib.SMTP_SSL('gator4021.hostgator.com')
        s.set_debuglevel(True) # debug
        s.login('email@pocketlobby.org', 'u23@$k4WzEcQVk*kdcRWxh*f^q')
        return s

class TallyMail(GenericMailer):
    """Send an email to a constituent"""
    subject = "Your Vote Matches"
    testing_destination_email_addresses = ['bryce@bridgetownint.com',
                                           'thea.briggs@gmail.com']

    def __init__(self, to, msg_text, msg_html, test=False, subject=None):
        """Create a new TallyMail instance

        params:

        to (string) = email address of recipient
        msg_text (string) = a plain text (ascii) message to send
        msg_html (string) = HTML formatted message to send
        subject (string) = the subject of the message
        """

        self.msg_text = msg_text
        self.msg_html = msg_html

        if test:
            self.to = {"email" : "bryce@bridgetownint.com",
                       "first_name" : "Bryce2"
                    }
        else:
            self.to = to

        if subject:
            self.subject = subject

        if test:
            self.subject = "[TEST] - %s" % self.subject

    def send(self):
        """Orchestraion of creating the message in email format, connecting to
        SMTP and sending the message"""

        msg = self._compose_message()
        s = self._connect_to_smtp()

        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(self.email_from, self.to['email'], msg.as_string())
        s.quit()

    def _compose_message(self):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.email_from
        msg['To'] = self.to['email']

        part1 = MIMEText(self.msg_text, 'plain')
        part2 = MIMEText(self._email_html_body(), 'html')

        msg.attach(part1)
        msg.attach(part2)
        return msg

    def _email_html_body(self):
        return self._email_body_head() + self.msg_html + self._email_body_tail()

    def _email_body_head(self):
        return """
        <html>
            <head></head>
            <body>
            <p> Hi %s,</p>

            <p> Below is a breakdown of how you voted last week and how you were represented. Some of the bills you voted on have not yet made it to the Senate or House, so some votes from last week may only in a later tally: </p>
        """ % self.to['first_name']

    def _email_body_tail(self):
        return """
          <p> We're working to improve this tally, so keep an eye out for new features and let us know if anything above seems out of place - we will fix any bugs you catch!</p>

          <h3>What happens next?</h3>
          <p>Using your selected pledge amount, we'll send you a Venmo request for each matched vote listed above - keep an eye out for a separate email inviting you to the Pocket Lobby Venmo group. Remember, this is an estimation not an obligation! If the request is not the right size donation for you this week, please feel free to make any donation that works for you and update your pledge amount if you'd like. </p>

          <p>Your donations will not go to your Representative or Senators, it will only be given in their name to cover party obligations. We will do our best to keep you informed about which funds they've selected for Pocket Lobby donations over time. We will be contacting your Representatives and Senators shortly, and donations will accrue until they have selected a destination fund for Pocket Lobby donations. If you'd like to help contact your Representatives and Senator with us, let us know!</p>

          <p>Thanks, <br />
          Team Pocket Lobby</p>

          </body>
          </html>
        """