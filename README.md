# Pocket Lobby - Sausage

> How the work gets done

## Getting started

`source activate pocketlobby_sausage`

We'd love your help! Be sure to see our [code of conduct](docs/code-of-conduct.md) and
[contributor guidelines](docs/CONTRIBUTING.md) before submitting code for this project.

## New Constituents

New users will join the mailing list from time to time during this alpha development period. For now, they need
a unique token to more anonymously log their opinions on votes. When a new user is added to the list, run the following
to create, and store, a unique token to their email address in MailChimp:

```bash
docker-compose run --rm cron_user_tokenization
```

## Legislative Bill Votes

Update vote records in the database by calling

```bash
docker-compose run --rm cron_load_legislator_votes
```

This will examine the votes contained in the `bills` table, create vote records
and then create records for individual legislators' votes.

## Bill Categories

Bill categories are subjects of bills. This app cares about them insofar as it
helps us develop a rudimentary preference ranking. After updating Bill Votes by
legislators, populate the bill's categories:

```bash
docker-compose run --rm cron_populate_bill_categories
```

## Vote Tallies

At the conclusion of a voting session, we compare the constituent's
votes on a bill to the representative's votes on a bill and then send
the constituent an email revealing their vote matching status.

Any new votes that either a constituent or a legislator provides are included as
part of the tally email if the vote has been updated since the last time the
constituent was sent a notification.

To send vote tallies to constituents, refresh sausage's records of constituent
votes (NOTE: do this after parsing the Google Form):


```bash
docker-compose run --rm  daemon_tally_queue_import
```

Send the emails using the `--test` flag first! Double check the results.

Then, to actually send the emails:

```bash
docker-compose run --rm cron_send_tally_mails
```

## Database

Database migrations managed via [Flyway](https://flywaydb.org/). To get
started, copy pocketlobby-fw.conf.sample to pocketlobby-fw.conf . Update
parameters in the configuration for your development environment.

### To migrate

In a console in the project root directory, run:
`flyway migrate -configFile=pocketlobby-fw.conf`

## TODO:

+ [ ] hr4300 passed in an unusual way. Support that method of passage
