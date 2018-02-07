"""
Import legislators from YAML file to a SQL database

NOTE: the migration for the legislators table is V0.0.7

https://github.com/unitedstates/congress-legislators maintains a list of current and past legislators. It is well
maintained. Thanks be to the committers of that project.

Update the repo on the local file system and then reference the appropriate files. The files have a standardized
format.

This solution is not very scalable but the need to update legislators is not frequent.

Run this with: ENV=development python -m utilities.import_legislators utilities/import_legislators.py
"""


import yaml
from dateutil.parser import parse as date_parse

from utilities.db import DB

current_leg_file = "/media/brycemcd/bkp/congress/congress-legislators/legislators-current.yaml"
historical_leg_file = "/media/brycemcd/bkp/congress/congress-legislators/legislators-historical.yaml"

db = DB()
query = """
    INSERT INTO representatives
    (bioguide_id, lis_id, first_name, last_name, type, party, state, district, chamber_begin_dt, chamber_end_dt) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (bioguide_id) DO UPDATE SET
        lis_id = excluded.lis_id,
        first_name = excluded.first_name,
        last_name = excluded.last_name,
        type = excluded.type,
        party = excluded.party,
        state = excluded.state,
        district = excluded.district,
        chamber_begin_dt = excluded.chamber_begin_dt,
        chamber_end_dt = excluded.chamber_end_dt
"""

def tenure_min_and_max(record):
    """
    Calculate the legislator's term time for the time that person has been in their current chamber

    :param record:
    :return: (oldest_date, term_expiration_date)

    There are a LOT of cases that aren't covered here. Legislators can start their careers in the house and then move
    to the senate or vise versa. They can also take legislative terms off. The immediate need is to calculate the
    earliest date and the term end date of the legislator in the chamber they currently serve.
    """

    # NOTE: this is the default date for the column in the database
    unknown_term_date = '2900-12-31'

    term_type = 'sen' if record['id'].get('lis', None) else 'rep'

    term_dates = []
    [term_dates.extend([date_parse(term['start']), date_parse(term['end'])])
     for term in record['terms'] if term['type'] == term_type]

    early_date = min(term_dates) if term_dates else unknown_term_date
    late_date = max(term_dates) if term_dates else unknown_term_date

    return (early_date, late_date)

def insert_into_db_from_yaml_record(record):
    """Given a yaml representation of one legislator, write it to the database"""

    most_recent_term = record['terms'][ len(record['terms']) - 1 ]
    district = None if most_recent_term['type'] == 'sen' else most_recent_term['district']

    early_date, late_date = tenure_min_and_max(record)

    insert_tuple = (
        record['id']['bioguide'],
        record['id'].get('lis', None),
        record['name']['first'],
        record['name']['last'],
        most_recent_term['type'],
        most_recent_term.get('party', "Unknown"), # this happens more closer to the revolution
        most_recent_term['state'],
        district,
        early_date,
        late_date
    )

    db.execute(query, insert_tuple)
    print(".", end="")

def import_current_legislators():
    print("Current Legislators")
    with open(current_leg_file) as leg_file:
        yaml_record = yaml.safe_load(leg_file)

        for i in range(len(yaml_record)):
            insert_into_db_from_yaml_record(yaml_record[i])

    print("done!")

def import_historical_legislators():
    print("Historical Legislators")
    with open(historical_leg_file) as leg_file:
        yaml_record = yaml.safe_load(leg_file)

        for i in range(len(yaml_record)):
            insert_into_db_from_yaml_record(yaml_record[i])

    print("done!")

def import_all_legislators():
    import_current_legislators()
    import_historical_legislators()

if __name__ == "__main__":
    print("starting...")
    import_current_legislators()
    print("") # the last print statement would have printed a . with no newline
    import_historical_legislators()
    print("") # the last print statement would have printed a . with no newline
    print("ALL DONE")
