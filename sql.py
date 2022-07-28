#!/usr/bin/env python3

import os
from pprint import pprint

import dotenv

import sqlalchemy
from src import utils
from src.utils import database

def main():
    dotenv.load_dotenv()

    engine = sqlalchemy.create_engine(
        os.environ['DB_URL'], #echo=True
    )
    db = database.get_instance(engine)
    user = db.get_user_by_ref('user1')
    user = db.get_user_by_id(user.ID)
    pprint(db.get_group_hierarchy(user.OID, 'A', flatten=True))
    # for row in db.get_schedules_for_user(user['ID'], utils.parse_date('2022-07-27')):
    #     pprint({ **row })
    # for row in db.get_schedules_for_user(user['ID'], utils.parse_date('2022-08-03')):
    #     pprint({ **row })
    # for row in db.get_schedules_for_user(user['ID'], utils.parse_date('2022-07-29')):
    #     pprint({ **row })

if __name__ == "__main__":
    main()