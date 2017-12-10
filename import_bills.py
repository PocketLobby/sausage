#!/usr/bin/env python

import argparse
from bill_updater.tracked_bill import TrackedBill

parser = argparse.ArgumentParser(description="Import bills into database")

parser.add_argument('bills', metavar="bill", type=str, nargs='+',
                    help="Bill to import in hr123 format (no -115)")

parser.add_argument('--test', action='store_true',
                    help="if enabled, a write to the database does not occur")

args = parser.parse_args()


if args.test:
    print("[ TEST MODE ]")

print("Creating summaries for %s" % args.bills)

for bill in args.bills:
    print("importing %s" % bill)
    bill = TrackedBill(bill)

    if not args.test:
        bill.upsert()


