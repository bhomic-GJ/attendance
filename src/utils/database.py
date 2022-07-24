"""

    database.py
    ~~~~~~~~~~~

    Provides an abstraction over the database interaction, by providing
    a class using a Singleton pattern to perform database operations
    abstracted as functions.

"""

import sqlalchemy
from sqlalchemy import sql

__INSTANCE__ = None

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
                            transaction.execute(*query)
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

    def remove_user_associations(self, user_id):
        query1 = self.membership.delete().where(self.membership.c.ID == user_id)
        query2 = self.attendance.delete().where(self.attendance.c.ID == user_id)
        self.execute(( (query1, {}), (query2, {}) ))

    def get_user_role(self, user_id):
        query = sql.select([ self.admin ]).where(self.admin.c.ID == user_id)
        result = self.execute(query)[0].fetchone()
        return 'admin' if result else 'non-admin'

    def get_organization_codes(self):
        query = sql.select([ self.organization.c.Code ])
        result = self.execute(query)[0].fetchall()
        return [ row.Code for row in result ]

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

    def get_group_hierarchy(self, organization, root_group=None):
        hierarchy = {}
        queue = [ (root_group, hierarchy) ]
        while len(queue) > 0:
            group, href = queue.pop(0)
            children = self.get_subgroups(organization, group)
            for child in children:
                href[child] = {}
                queue.append( ( child, href[child] ) )
        return hierarchy

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
            href['members'] = self.get_members(organization, group)
            children = self.get_subgroups(organization, group)
            for child in children:
                href['children'][child] = { 'children': {}, 'members': None }
                queue.append( ( child, href['children'][child] ) )
        return hierarchy

    def do_nothing(self):
        pass

def get_instance(database_engine):
    """ Returns the current instance of the AttendanceDatabase abstraction. """
    # pylint: disable=global-statement
    global __INSTANCE__
    if not __INSTANCE__:
        __INSTANCE__ = AttendanceDatabase(database_engine)
    return __INSTANCE__