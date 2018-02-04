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

from utilities.db import DB

current_leg_file = "/media/brycemcd/bkp/congress/congress-legislators/legislators-current.yaml"
historical_leg_file = "/media/brycemcd/bkp/congress/congress-legislators/legislators-historical.yaml"

db = DB()
query = """
    INSERT INTO legislators_new
    (bioguide_id, lis_id, first_name, last_name, type, party, state, district) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)
"""

def insert_into_db_from_yaml_record(record):
    """Given a yaml representation of one legislator, write it to the database"""

    most_recent_term = record['terms'][ len(record['terms']) - 1 ]
    district = None if most_recent_term['type'] == 'sen' else most_recent_term['district']

    insert_tuple = (
        record['id']['bioguide'],
        record['id'].get('lis', None),
        record['name']['first'],
        record['name']['last'],
        most_recent_term['type'],
        most_recent_term.get('party', "Unknown"), # this happens more closer to the revolution
        most_recent_term['state'],
        district)

    db.execute(query, insert_tuple)
    print(".", end="")

print("Current Legislators")
with open(current_leg_file) as leg_file:
    yaml_record = yaml.safe_load(leg_file)

    for i in range(len(yaml_record)):
        insert_into_db_from_yaml_record(yaml_record[i])

print("") # the last print statement would have printed a . with no newline
print("Historical Legislators")
with open(historical_leg_file) as leg_file:
    yaml_record = yaml.safe_load(leg_file)

    for i in range(len(yaml_record)):
        insert_into_db_from_yaml_record(yaml_record[i])

print("done!")