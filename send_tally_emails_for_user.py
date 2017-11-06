#!/usr/bin/env python

import psycopg2
import pandas as pd

import constituent_vote_tally.vote_tally as vt
import constituent_emails.tally_mail as tm

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
        ]

bills = [full+ "-115" for full in bills]

vto = vt.VoteTally(bills)

# TODO: put these into env vars
conn = psycopg2.connect(host='psql01.thedevranch.net',
    user='pl_reporting',
    database='pocketlobby')

all_constituents = pd.read_sql("SELECT * FROM constituents", conn, index_col='id')

for constituent in all_constituents.to_dict('records'):
    vote_table = vto.create_html_comparison_table(constituent['user_token'])

    subject = constituent['first_name'].capitalize() + "'s Vote Matches"
    mailer = tm.TallyMail('bryce@bridgetownint.com', vote_table, vote_table, subject)
    print(mailer.send())
    break

