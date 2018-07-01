"""
When a user is added to the system, they are added via Mailchimp (Constituent
_will_ eventually handle all this). Poll MC and add user tokens as new users
are added.
"""

import string
import random
from mailchimp3 import MailChimp
from utilities.configurator import Configurator

config = Configurator().config

PL_LIST_ID = config['mailchimp_leg_update_list_id']

MC_CLIENT = MailChimp(mc_api=config['mailchimp_api_token'])

# FIXME: won't scale, but we don't need it to right now. 100 users is our goal
# for the end of 2018
def get_all_members():
    """
    Fetch all users from MC

    :return: api response obj
    """
    mems_api_response = MC_CLIENT.lists.members.all(PL_LIST_ID,
                                                    count=250,
                                                    offset=0)

    assert mems_api_response['total_items'] < 250

    return mems_api_response

def all_tokens(mems):
    """
    all user existing tokens returned as a list
    :param mems: RAW API response of all members
    :return: list of tokens
    """

    return [user['merge_fields']['USER_TOKEN'] for user in mems['members']]


def generate_token():
    """
    generates a random token suitable for identifying a MC subscriber

    :return: String:
    """

    rando = lambda : ''.join(random.choice(string.ascii_letters) for _ in range(5))
    return rando() + '-' + rando()


def main():
    """
    The Glue. Creates a unique user token for a member without one

    :return: None. Prints like crazy
    """

    print("Fetching users, populating tokens if they don't have one")
    mems = get_all_members()
    existing_user_tokens = all_tokens(mems)

    for user in mems['members']:
        if user['merge_fields']['USER_TOKEN'] == '':
            print(user['email_address'])
            token = generate_token()
            while token in existing_user_tokens:
                token = generate_token()
            print("token is: %s" % token)
            MC_CLIENT.lists.members.update(list_id=PL_LIST_ID,
                                           subscriber_hash=user['id'],
                                           data={
                                               'merge_fields': {
                                                   'USER_TOKEN': token
                                               }
                                           })


if __name__ == "__main__":
    main()