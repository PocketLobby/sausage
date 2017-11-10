#!/usr/bin/env python

import sys
import re
import psycopg2
import pandas as pd

import constituent_emails.tally_mail as tm
from constituent_emails import vote_tally as vt

import argparse

parser = argparse.ArgumentParser(description='Send tally emails to constituents')

parser.add_argument('bills', metavar='bill_id', nargs='+',
        help='A list of bills to send tallies for i.e. hr123 or s345')

args = parser.parse_args()

for bill in args.bills:
    if not re.match(r"(hr|s|hjres)(\d{1,})", bill):
        print("""
        A bill must be in the format: hrX, sX or hjresX. %s does
        not meet those formatting requirements.
        """ % bill)

        sys.exit(1)

sys.exit(1)

bills = [
        'hr378',
        'hr3031',
        'hr2196',
        'hr3243',
        'hr2763',
        's190',
        's920',
        'hr2302',
        'hr2229',
        'hr2989',
        's585',

        'hr2824',
        'hjres111',
        ]

bills = [full+ "-115" for full in args.bills]

vto = vt.VoteTally(bills)

# TODO: put these into env vars
conn = psycopg2.connect(host='psql01.thedevranch.net',
     user='pl_reporting',
     database='pocketlobby')

all_constituents = pd.read_sql("SELECT * FROM constituents LIMIT 2 OFFSET 4", conn, index_col='id')

for constituent in all_constituents.to_dict('records'):
    vote_table = vto.create_html_comparison_table(constituent['user_token'])

    subject = constituent['first_name'].capitalize() + "'s Vote Matches"
    mailer = tm.TallyMail('bryce@bridgetownint.com', vote_table, vote_table, subject)
    print(mailer.send())
    break
