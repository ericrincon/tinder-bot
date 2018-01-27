import argparse

import pandas as pd

from tinder.database.models import TinderUser
from tinder.database import Session

def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--output', default='bios.csv')

    session = Session()

    all_users = session.query(TinderUser).all()

    users_dict_df = {
        'name': [user.name for user in all_users],
        'age': [user.age for user in all_users],
        'bio': [user.bio for user in all_users]
    }


    users_df = pd.DataFrame(users_dict_df)
    users_df.to_csv('Tinderusers.csv')

if __name__ == '__main__':
    main()
