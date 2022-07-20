import sqlalchemy

__INSTANCE__ = None

class AttendanceDatabase:
    """ Minimal abstraction over the attendance database. """
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
                    return [
                        connection.execute(*query)
                        for query in queries
                    ]
                

def get_instance(database_engine):
    """ Returns the current instance of the AttendanceDatabase abstraction. """
    global __INSTANCE__
    if not __INSTANCE__:
        __INSTANCE__ = AttendanceDatabase(database_engine)
    return __INSTANCE__