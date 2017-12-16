#!/usr/bin/env python

from time import sleep
import argparse
import pandas as pd

from vote_tallies.tally_mail import TallyMail
from vote_tallies import cons_vote_tally as vt
from vote_tallies.cons_vote_tally import DB
from vote_tallies.cons_vote_tally import ConsVoteTally


parser = argparse.ArgumentParser(description='Send tally emails to constituents')

parser.add_argument('--no-email', action='store_true',
        help='When provided, no emails will be sent')

parser.add_argument('--test', action='store_true',
        help='A list of bills to send tallies for i.e. hr123 or s345')

args = parser.parse_args()


if args.test:
    print("[ TEST MODE ]")

print("Creating summaries for %s" % vto.bills)

conn = DB.conn

#all_constituents = pd.read_sql("SELECT * FROM constituents LIMIT 2 OFFSET 4", conn, index_col='id')
all_constituents = pd.read_sql("SELECT * FROM constituents", conn, index_col='id')

participants = []
non_participants = []

for constituent in all_constituents.to_dict('records'):
    cvt = ConsVoteTally(constituent['id'])
    bills = cvt.get_bill_updated_since_last_notification()
    vto = vt.VoteTally(bills)
    vote_table = vto.create_html_comparison_table(constituent['user_token'])

    if not vote_table:
        non_participants.append(constituent['first_name'])
        print("x", end='')
        #print("%s did not participate in this campaign" % constituent['first_name'])
        continue

    participants.append(constituent['first_name'])
    print(".", end='')

    if not args.no_email:
        # for recipient in to:
        to = {'email' : constituent['email'],
              'id'    : constituent['id'],
              'first_name' : constituent['first_name'],
              }

        mailer = TallyMail(to, vote_table, vote_table, test=args.test)
        print(mailer.send())
        # NOTE: I'm getting a connection refused error. Rate limit this shiz
        sleep(5.00)

print("")
print("participants: %s" % participants)
print("non participants: %s" % non_participants)
