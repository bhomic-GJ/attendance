#!/usr/bin/env python3

import os
from pprint import pprint
import datetime

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
    # params = {
    #     'Creator'          : user.ID,
    #     'GName'            : 'A',
    #     'Start_Time'       : utils.format_date(utils.parse_time('06:30:00.000Z'), "%H:%M:%S"),
    #     'End_Time'         : utils.format_date(utils.parse_time('10:30:00.000Z'), "%H:%M:%S"),
    #     'Commencement_Date': utils.parse_date('2022-07-28T07:34:15.000Z'),
    #     'OID'              : user.OID,
    #     'Title'            : 'Presentation Discussion',
    #     'Status'           : '0',
    #     'Frequency'        : '1'
    # }

    # db.execute((db.schedule.insert(), params))

    # pprint(db.get_schedule(user.OID, 'A', utils.parse_time('06:30:00.000Z'), utils.parse_date('2022-07-28')))
    # pprint(db.get_group_hierarchy(user.OID, 'A', flatten=True))
    for row in db.get_attendance_record("61c8d38d-2c9e-4197-998e-0ef01eb3488c", "A", utils.parse_time('10:30:00'), utils.parse_date('2022-07-28'), utils.parse_date('2022-08-03')):
        pprint({ **row })
    for row in db.get_schedules_for_user(user['ID'], utils.parse_date('2022-07-28')):
        pprint({ **row })
    # for row in db.get_schedules_for_user(user['ID'], utils.parse_date('2022-08-03')):
    #     pprint({ **row })
    # for row in db.get_schedules_for_user(user['ID'], utils.parse_date('2022-07-29')):
    #     pprint({ **row })

if __name__ == "__main__":
    obj1={'OID': '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'Start_Time': datetime.time(10, 30), 'Commencement_Date': datetime.datetime(2022, 7, 28, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(0), 'UTC')), 'Creator': '93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a', 'GName': 'A', 'Token': 'MjAyMi0wNy0yOCAwMDowMDowMCswMDowMDEwOjMwOjAwQTpdoDuYNlpGQqZ6TKwK3W0hOgAJhJIOZRHtsOeCd-RU_vE=-dCYSnq6TbR7UA'}
    obj2={'OID': '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'Start_Time': datetime.time(10, 30), 'Commencement_Date': datetime.datetime(2022, 7, 28, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(0), 'UTC')), 'Creator': '93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a', 'GName': 'A', 'Token': 'MjAyMi0wNy0yOCAwMDowMDowMCswMDowMDEwOjMwOjAwQTpdoDuYNlpGQqZ6TKwK3W0hOgAJhJIOZRHtsOeCd-RU_vE=-dCYSnq6TbR7UA'}
    print(obj1 == obj2)
    main()