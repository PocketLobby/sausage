# Pocket Lobby - Sausage

> How the work gets done

## Getting started

`source activate pocketlobby_sausage`

## Vote Tallies

At the conclusion of a voting session, we compare the constituent's
votes on a bill to the representative's votes on a bill and then send
the constituent an email revealing their vote matching status.

Any new votes that either a constituent or a legislator provides are included as
part of the tally email if the vote has been updated since the last time the
constituent was sent a notification.

To send vote tallys to constituents, run this command:

` ENV=production ./send_tally_emails_for_user.py --email`

## Database

Database migrations managed via [Flyway](https://flywaydb.org/). To get
started, copy pocketlobby-fw.conf.sample to pocketlobby-fw.conf . Update
parameters in the configuration for your development environment.

### To migrate

In a console in the project root directory, run:
`flyway migrate -configFile=pocketlobby-fw.conf`

## TODO:

+ [ ] hr4300 passed in an unusal way. Support that method of passage
