#!/usr/bin/env python

import argparse
from vote_tallies.cmd_send_tally_emails import CmdSendTallyEmails


parser = argparse.ArgumentParser(description='Send tally emails to constituents')

parser.add_argument('--email', action='store_true',
        help='When provided, no emails will be sent')

parser.add_argument('--test', action='store_true',
        help='A list of bills to send tallies for i.e. hr123 or s345')

args = parser.parse_args()

if args.test:
    print("[ TEST MODE ]")

CmdSendTallyEmails.send_tally_emails(args)
