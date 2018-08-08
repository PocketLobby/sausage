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
docker run -it --rm --name sausage -v $(pwd):/opt/project sausage /bin/bash
python -m utilities.new_user_tokenizer utilities/new_user_tokenizer.py
```

## Vote Tallies

At the conclusion of a voting session, we compare the constituent's
votes on a bill to the representative's votes on a bill and then send
the constituent an email revealing their vote matching status.

Any new votes that either a constituent or a legislator provides are included as
part of the tally email if the vote has been updated since the last time the
constituent was sent a notification.

To send vote tallies to constituents, first refresh sausage's records of votes:


```bash
# NOTE: docker-compose this
docker run -it --rm --name sausage -v $(pwd):/opt/project --env-file=prod_tally_mail.env -v /home/brycemcd/Sites/congress/data/:/var/congress/data/ sausage python load_legislator_votes.py
```

`python -u ./send_tally_emails_for_user.py --email --test`

## Legislative Bill Votes

Update vote records in the database by calling

`ENV=production ./load_legislator_votes.py`

This will examine the votes contained in the `bills` table, create vote records
and then create records for individual legislators' votes.

## Database

Database migrations managed via [Flyway](https://flywaydb.org/). To get
started, copy pocketlobby-fw.conf.sample to pocketlobby-fw.conf . Update
parameters in the configuration for your development environment.

### To migrate

In a console in the project root directory, run:
`flyway migrate -configFile=pocketlobby-fw.conf`

## TODO:

+ [ ] hr4300 passed in an unusual way. Support that method of passage
