#!/usr/bin/env python

from random import randint
from time import sleep
import argparse
import pandas as pd
import psycopg2
import re
import sys

from vote_tallies.tally_mail import TallyMail
from vote_tallies import vote_tally as vt
from vote_tallies.vote_tally import DB


parser = argparse.ArgumentParser(description='Send tally emails to constituents')

parser.add_argument('bills', metavar='bill_id', nargs='?',
        help='A list of bills to send tallies for i.e. hr123 or s345')

parser.add_argument('--no-email', action='store_true',
        help='When provided, no emails will be sent')

parser.add_argument('--test', action='store_true',
        help='A list of bills to send tallies for i.e. hr123 or s345')

args = parser.parse_args()

bill = args.bills # NOTE: remove the next line if args are needed
bills = [
        'hr2921',
        'hr2941',
        'hr3567',
        'hr2521',
        'hr3903',
        'hr1585',
        'hr3279',
        'hr1074',
        'hr425',
        'hr849',
        ]

for bill in bills:
    if not re.match(r"(hr|s|hjres)(\d{1,})", bill):
        print("""
        A bill must be in the format: hrX, sX or hjresX. %s does
        not meet those formatting requirements.
        """ % bill)

        sys.exit(1)


bills = [full+ "-115" for full in bills]

vto = vt.VoteTally(bills)

if args.test:
    print("[ TEST MODE ]")

print("Creating summaries for %s" % vto.bills)

conn = DB.conn

#all_constituents = pd.read_sql("SELECT * FROM constituents LIMIT 2 OFFSET 4", conn, index_col='id')
all_constituents = pd.read_sql("SELECT * FROM constituents", conn, index_col='id')

participants = []
non_participants = []

for constituent in all_constituents.to_dict('records'):
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
        to = {'email' : 'bryce+test@bridgetownint.com',
              'first_name' : 'Bryce',}

        mailer = TallyMail(to, vote_table, vote_table, test=args.test)
        print(mailer.send())
        # NOTE: I'm getting a connection refused error. Rate limit this shiz
        sleep(5.00)
    break

print("")
print("participants: %s" % participants)
print("non participants: %s" % non_participants)
