"""

    database.py
    ~~~~~~~~~~~

    Provides an abstraction over the database interaction, by providing
    a class using a Singleton pattern to perform database operations
    abstracted as functions.

"""

import enum

import sqlalchemy
from sqlalchemy import sql

__INSTANCE__ = None

class EventStatus(enum.Enum):
    ONE_TIME = 0
    RECURRING = 1

class AttendanceDatabase:
    """ Minimal abstraction over the attendance database """

    def __init__(self, database_engine):
        self.engine          = database_engine
        self.meta            = sqlalchemy.MetaData(database_engine)

        self.active_schedule = sqlalchemy.Table('ACTIVE_SCHEDULE', self.meta, autoload=True)
        self.admin           = sqlalchemy.Table('ADMIN'          , self.meta, autoload=True)
        self.attendance      = sqlalchemy.Table('ATTENDANCE'     , self.meta, autoload=True)
        self.group           = sqlalchemy.Table('GROUP'          , self.meta, autoload=True)
        self.group_hierarchy = sqlalchemy.Table('GROUP_HIERARCHY', self.meta, autoload=True)
        self.membership      = sqlalchemy.Table('MEMBERSHIP'     , self.meta, autoload=True)
        self.organization    = sqlalchemy.Table('ORGANIZATION'   , self.meta, autoload=True)
        self.schedule        = sqlalchemy.Table('SCHEDULE'       , self.meta, autoload=True)
        self.user            = sqlalchemy.Table('USER'           , self.meta, autoload=True)

    def execute(self, *queries):
        """ Executes the given set of queries, or a set of query sets.
            This method operates in two modes:
            - If given a set of query parameter tuples passed as positional arguments,
                the queries are executed as a single transaction.
            - If given a set of query sets, with each query set being a collection of
                query tuples, each query set is executed as a single transaction.
            Query tuples consist of a parameterized SQL query object and the set of parameters
            to bind with the query during execution as a dictionary.

        Returns:
            list[sqlalchemy.LegacyCursorResult]: Results of the queries for a single transaction.
            list[list[sqlalchemy.LegacyCursorResult]]: Results of the queries for multiple transactions.
        """
        if len(queries) == 0: return

        with self.engine.begin() as connection:
            if isinstance(queries[0], (list, tuple)) and \
                isinstance(queries[0][0], (list, tuple)):
                result = []
                for atomic_queries in queries:
                    with connection.begin() as transaction:
                        result.append([
                            connection.execute(*query)
                            for query in atomic_queries
                        ])
                return result
            else:
                with connection.begin():
                    if isinstance(queries[0], (list, tuple)):
                        return [
                            connection.execute(*query)
                            for query in queries
                        ]
                    else:
                        return [
                            connection.execute(query)
                            for query in queries
                        ]

    # Query abstractions:

    def get_user_by_id(self, user_id):
        query = sql.select([ self.user ]) \
            .where(self.user.c.ID == user_id).limit(1)
        return self.execute(query)[0].fetchone()

    def get_user_by_ref(self, username_or_email):
        query = sql.select([
            self.user.c.ID,
            self.user.c.Username,
            self.user.c.Password_Hash,
            self.user.c.Password_Salt
        ]).where(
            (self.user.c.Username == username_or_email) |
            (self.user.c.Email == username_or_email)
        ).limit(1)
        return self.execute(query)[0].fetchone()

    def get_organization_by_id(self, organization_id):
        query = sql.select([ self.organization ]) \
            .where(self.organization.c.OID == organization_id).limit(1)
        return self.execute(query)[0].fetchone()

    def get_organizations(self):
        return self.execute(sql.select([ self.organization ]))[0].fetchall()

    def remove_user_associations_and_migrate(self, user_id, org_id=None):
        query1 = self.membership.delete().where(self.membership.c.ID == user_id)
        query2 = self.attendance.delete().where(self.attendance.c.ID == user_id)
        params = { 'OID': org_id }
        if org_id: params['OJoin_Date'] = sql.func.now()
        query3 = self.user.update().where(self.user.c.ID == user_id).values(**params)
        self.execute(( (query1, {}), (query2, {}), (query3, {}) ))

    def get_user_role(self, user_id):
        query = sql.select([ self.admin ]).where(self.admin.c.ID == user_id)
        result = self.execute(query)[0].fetchone()
        return 'admin' if result else 'non-admin'

    def get_organization_codes(self):
        query = sql.select([ self.organization.c.Code ])
        result = self.execute(query)[0].fetchall()
        return [ row.Code for row in result ]

    def set_user_role(self, user_id, role):
        if role == 'non-admin':
            query = self.admin.delete().where(self.admin.c.ID == user_id)
        else:
            query = self.admin.insert().values(ID=user_id)
        return self.execute(query)[0].rowcount == 1

    def update_user(self, user_id, params):
        if 'OID' in params: params['OJoin_Date'] = sql.func.now()
        if 'ID' in params: del params['ID']
        query = self.user.update().where(self.user.c.ID == user_id).values(**params)
        result = self.execute(query)[0]
        return result.rowcount == 1

    def get_groups_by_organization(self, organization):
        query = sql.select([ self.group ]).where(self.group.c.OID == organization)
        return self.execute(query)[0].fetchall()

    def get_subgroups(self, organization, group_name=None):
        children_query = sql.select([
            self.group.c.Name, self.group.c.OID,
            self.group_hierarchy.c.Parent,
        ]) \
        .select_from(
            self.group.join(
                self.group_hierarchy,
                onclause=(
                    (self.group_hierarchy.c.OID == self.group.c.OID) &
                    (self.group_hierarchy.c.Name == self.group.c.Name)
                ),
                isouter=True
            )
        ) \
        .where(
            (self.group_hierarchy.c.Parent == group_name) &
            (self.group.c.OID    == organization)
        ) \
        .order_by(self.group_hierarchy.c.Name.asc())
        result = self.execute(children_query)[0]
        return [ row.Name for row in result.fetchall() ]

    def get_parent_chain(self, organization, group, include_root=True):
        group_list = [ group ]
        while True:
            pgroup = self.execute(sql.select([ self.group_hierarchy.c.Parent ]).where(
                (self.group_hierarchy.c.Name == group) &
                (self.group_hierarchy.c.OID == organization)
            ))[0].fetchone()
            if not pgroup:
                if include_root:
                    group_list.append(pgroup)
                break
            group_list.append(pgroup)
        return group_list

    def get_user_groups(self, user_id):
        query = sql.select([ self.membership.c.GName, self.membership.c.OID ]).where(self.membership.c.ID == user_id)
        start_groups = set((row.GName, row.OID) for row in self.execute(query)[0].fetchall())
        groups = set()
        for group, OID in start_groups:
            groups |= set(self.get_parent_chain(OID, group, include_root=False))
        return groups

    def get_group_hierarchy(self, organization, root_group=None, flatten=False):
        hierarchy = {}
        queue = [ (root_group, hierarchy) ]
        while len(queue) > 0:
            group, href = queue.pop(0)
            children = self.get_subgroups(organization, group)
            for child in children:
                href[child] = {}
                queue.append( ( child, href[child] ) )
        if not flatten:
            return hierarchy
        else:
            linear_hierarchy = [ root_group ]
            queue = [ (root_group, hierarchy) ]
            while len(queue) > 0:
                group, href = queue.pop(0)
                linear_hierarchy.extend(hierarchy.keys())
                for child in children:
                    queue.append( ( child, href[child] ) )
            return linear_hierarchy

    def get_members(self, organization, group_name=None):
        if group_name:
            query = sql.select([
                    self.user.c.ID,
                    self.user.c.Name,
                    self.user.c.Email,
                    self.user.c.Contact,
                    sqlalchemy.case(
                        (self.admin.c.ID.is_(None), 'non-admin'),
                        else_ = 'admin'
                    ).label('Role')
                ]).select_from(
                    self.membership.join(
                        self.user, (self.user.c.ID == self.membership.c.ID),
                    ).join(
                        self.admin, (self.admin.c.ID == self.user.c.ID), isouter=True
                    )
                ).where(
                    (self.membership.c.GName == group_name) &
                    (self.membership.c.OID == organization)
                ).order_by(sql.asc('Role'), self.user.c.Name.asc())
        else:
            query = sql.select([
                    self.user.c.ID,
                    self.user.c.Name,
                    self.user.c.Email,
                    self.user.c.Contact,
                    sqlalchemy.case(
                        (self.admin.c.ID.is_(None), 'non-admin'),
                        else_ = 'admin'
                    ).label('Role')
                ]).select_from(
                    self.user.join(
                        self.admin, self.user.c.ID == self.admin.c.ID, isouter=True
                    )
                ).where(
                (self.user.c.OID == organization) &
                ~ (
                    sql.select([ self.membership.c.ID ]).where(
                        (self.membership.c.OID == self.user.c.OID) &
                        (self.membership.c.ID == self.user.c.ID)
                    ).exists()
                )
            ).order_by(sql.asc('Role'), self.user.c.Name.asc())
        return self.execute(query)[0].fetchall()

    def get_member_hierarchy(self, organization, root_group=None):
        hierarchy = { 'children': {}, 'members': None }
        queue = [ (root_group, hierarchy) ]
        while len(queue) > 0:
            group, href = queue.pop(0)
            href['members'] = [ { **row } for row in self.get_members(organization, group) ]
            children = self.get_subgroups(organization, group)
            for child in children:
                href['children'][child] = { 'children': {}, 'members': None }
                queue.append( ( child, href['children'][child] ) )
        return hierarchy

    def get_active_schedule(self, organization, group, start_time, start_date):
        query = sql.select([ self.active_schedule, self.schedule.c.End_Time ])\
            .select_from(self.active_schedule.join(
                self.schedule,
                (self.active_schedule.c.OID == self.schedule.c.OID) &
                (self.active_schedule.c.GName == self.schedule.c.GName) &
                (self.active_schedule.c.Start_Time == self.schedule.c.Start_Time) &
                (self.active_schedule.c.Commencement_Date == self.schedule.c.Commencement_Date)
            ))\
            .where(self.active_schedule.c.OID == organization)\
            .where(self.active_schedule.c.GName == group)\
            .where(self.active_schedule.c.Start_Time == start_time.replace(tzinfo=None))\
            .where(self.active_schedule.c.Commencement_Date == start_date.replace(tzinfo=None)).limit(1)
        return self.execute(query)[0].fetchone()

    def get_schedule(self, organization, group, start_time, start_date):
        query = sql.select([ self.schedule ])\
            .where(self.schedule.c.OID == organization)\
            .where(self.schedule.c.GName == group)\
            .where(self.schedule.c.Start_Time == start_time.replace(tzinfo=None))\
            .where(self.schedule.c.Commencement_Date == start_date).limit(1)
        return self.execute(query)[0].fetchone()

    def can_activate_schedule(self, organization, group, creator, start_time, start_date, date):
        schedule = self.get_schedule(organization, group, start_time, start_date)
        if not schedule or schedule.Creator != creator: return False
        valid_date = schedule.Status == EventStatus.ONE_TIME.value and abs((schedule.Commencement_Date - date.date()).total_seconds()) < (24*3600)
        valid_date = valid_date or (schedule.Status == EventStatus.RECURRING.value and (date.date() - schedule.Commencement_Date).days % schedule.Frequency == 0)
        return valid_date and (schedule.Start_Time < date.time() < schedule.End_Time)

    def is_schedule_valid_on_date(self, organization, group, start_time, start_date, date):
        schedule = self.get_schedule(organization, group, start_time, start_date)
        if not schedule: return False
        valid_date = schedule.Status == EventStatus.ONE_TIME.value and abs((schedule.Commencement_Date - date.date()).total_seconds()) < (24*3600)
        valid_date = valid_date or (schedule.Status == EventStatus.RECURRING.value and (date.date() - schedule.Commencement_Date).days % schedule.Frequency == 0)
        return valid_date

    def delete_active_schedule(self, organization, group, creator, start_time, start_date):
        schedule = self.get_schedule(organization, group, start_time, start_date)
        if not schedule or schedule.Creator != creator: return 0
        query = self.active_schedule.delete()\
            .where(self.active_schedule.c.OID == organization)\
            .where(self.active_schedule.c.GName == group)\
            .where(self.active_schedule.c.Start_Time == start_time.replace(tzinfo=None))\
            .where(self.active_schedule.c.Commencement_Date == start_date.replace(tzinfo=None))
        return self.execute(query)[0].rowcount

    def get_schedule_attendance(self, organization, group, start_time, start_date, date):
        query = sql.select([ self.attendance, self.user.c.Name ])\
            .select_from(self.attendance.join(
                self.user, (self.attendance.c.ID == self.user.c.ID)
            ))\
            .where(self.attendance.c.OID == organization)\
            .where(self.attendance.c.GName == group)\
            .where(self.attendance.c.Start_Time == start_time.replace(tzinfo=None))\
            .where(self.attendance.c.Commencement_Date == start_date.replace(tzinfo=None))\
            .where(sql.func.datediff(date.replace(tzinfo=None), self.attendance.c.Record_Time) == 0)
        return self.execute(query)[0].fetchall()

    def get_attendance_record(self, organization, group, start_time, start_date, date):
        """
            WITH present_user (ID, GName, OID) as (Select ATTENDANCE.id, ATTENDANCE.Gname, ATTENDANCE.OID
                from ATTENDANCE, SCHEDULE where
                SCHEDULE.GName = ATTENDANCE.GName AND
                SCHEDULE.OID = ATTENDANCE.OID AND
                SCHEDULE.Start_Time = ATTENDANCE.Start_Time AND
                SCHEDULE.Commencement_Date = ATTENDANCE.Commencement_Date AND
                ATTENDANCE.GName = 'A' AND ATTENDANCE.OID = '61c8d38d-2c9e-4197-998e-0ef01eb3488c')
            SELECT MEMBERSHIP.ID, IF (MEMBERSHIP.ID = present_user.ID, 'Present', 'Absent') FROM MEMBERSHIP NATURAL LEFT OUTER JOIN present_user
        """
        groups = self.get_group_hierarchy(organization, group, flatten=True)
        group_users = sql.select([ self.membership ])\
            .where(self.membership.c.GName.in_(groups))\
            .where(self.membership.c.OID == organization).subquery()
        if not self.is_schedule_valid_on_date(organization, group, start_time, start_date, date):
            query = sql.select([
                group_users.c.ID, self.user.c.Name, sqlalchemy.case((1 == 0, '?'), else_='-').label('Record')
            ]).select_from(
                group_users.join( self.user, onclause=(self.user.c.ID == group_users.c.ID) )
            ).where( ~ (sql.select([ self.admin.c.ID ]).where(group_users.c.ID == self.admin.c.ID).exists()) )
        else:
            present_users = sql.select([ self.attendance ])\
                .where(self.attendance.c.OID == organization)\
                .where(self.attendance.c.GName == group)\
                .where(self.attendance.c.Start_Time == start_time.replace(tzinfo=None))\
                .where(self.attendance.c.Commencement_Date == start_date)\
                .where(sql.func.datediff(self.attendance.c.Record_Time, date.replace(tzinfo=None)) < 2).subquery()
            query = sql.select([
                group_users.c.ID, self.user.c.Name, sqlalchemy.case(
                    (group_users.c.ID == present_users.c.ID, 'P'), else_='A'
                ).label('Record')
            ]).select_from(
                group_users.join(
                    present_users, onclause=(group_users.c.ID == present_users.c.ID),
                    isouter=True
                ).join(
                    self.user, onclause=(self.user.c.ID == group_users.c.ID)
                )
            ).where( ~ (sql.select([ self.admin.c.ID ]).where(group_users.c.ID == self.admin.c.ID).exists()) )
        return self.execute(query)[0].fetchall()

    def get_schedule_members(self, organization, group):
        groups = self.get_group_hierarchy(organization, group, flatten=True)
        query = sql.select([ self.membership, self.user.c.Name ])\
            .select_from(self.membership.join(
                self.user, (self.membership.c.ID == self.user.c.ID)
            ))\
            .where(self.membership.c.GName.in_(groups))\
            .where(self.membership.c.OID == organization).subquery()
        return self.execute(query)[0].fetchall()

    def has_attendance_for_schedule(
        self, user_id, date, organization, group,
        start_time, start_date
    ):
        query = sql.select([ self.attendance ])\
            .where(self.attendance.c.ID == user_id)\
            .where(self.attendance.c.OID == organization)\
            .where(self.attendance.c.GName == group)\
            .where(self.attendance.c.Start_Time == start_time.replace(tzinfo=None))\
            .where(self.attendance.c.Commencement_Date == start_date.replace(tzinfo=None))\
            .where(sql.func.datediff(self.attendance.c.Record_Time, date) == 0)
        return self.execute(query)[0].fetchone() is not None

    def get_schedules_for_group(self, user_id, group):
        query = sql.select([ self.schedule, self.user.c.Name.label('CreatorName') ]) \
            .select_from(self.schedule.join(
                self.user, onclause=(self.user.c.ID == self.schedule.c.Creator)
            ))\
            .where(
                (self.schedule.c.OID == sql.select([ self.user.c.OID ])\
                    .where(self.user.c.ID == user_id).scalar_subquery()) &
                (self.schedule.c.GName == group)
            )
        return self.execute(query)[0].fetchall()

    def get_schedules_for_user(self, user_id, date):
        query = sql.select([ self.schedule, self.user.c.Name.label('CreatorName') ]) \
            .select_from(self.schedule.join(
                self.user, onclause=(self.user.c.ID == self.schedule.c.Creator)
            ))\
            .where(
                (self.schedule.c.OID == sql.select([ self.user.c.OID ])\
                    .where(self.user.c.ID == user_id).scalar_subquery())
            )\
            .where(
                (self.schedule.c.Creator == user_id) |
                (self.schedule.c.GName.in_(self.get_user_groups(user_id)))
            )
        result = list(self.execute(query)[0].fetchall())
        filtered_result = []
        for row in result:
            if row.Status == EventStatus.ONE_TIME.value and abs((row.Commencement_Date - date.date()).total_seconds()) < (24*3600):
                filtered_result.append(row)
            elif row.Status == EventStatus.RECURRING.value:
                if (date.date() - row.Commencement_Date).days % row.Frequency == 0:
                    filtered_result.append(row)
        return filtered_result

def get_instance(database_engine):
    """ Returns the current instance of the AttendanceDatabase abstraction. """
    # pylint: disable=global-statement
    global __INSTANCE__
    if not __INSTANCE__:
        __INSTANCE__ = AttendanceDatabase(database_engine)
    return __INSTANCE__