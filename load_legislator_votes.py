#!/usr/bin/env python

import argparse

from bill_updater.legislative_votes import LegislativeVotes

parser = argparse.ArgumentParser(description="Load votes that have been captured as activity in `bills` but don't have a vote record")

args = parser.parse_args()

LegislativeVotes.upsert_uncaptured_votes()
