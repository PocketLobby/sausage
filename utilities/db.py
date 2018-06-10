import psycopg2

from utilities.configurator import Configurator


class DataBaseEnvironmentConnection:
    """Provides connection details to the database given an environment"""


    config = Configurator().config

    @classmethod
    def conn(cls):
        """A Database Connection object. In test, this is None (use mocks!)"""

        # NOTE: I have yet to have a good reason to test that the db works
        if cls.config['ENV'] == 'test':
            return None

        return psycopg2.connect(host=cls.config['db_host'],
                                user=cls.config['db_user'],
                                database=cls.config['db_db'])


class DB:
    """Maintains a connection to the database and provides reusable methods for data fetching and writing"""

    conn = DataBaseEnvironmentConnection.conn()

    def execute(self, statement, interp=None):
        """Execute and commit a db statement"""

        # http://initd.org/psycopg/docs/usage.html#with-statement
        # manages commits/rollbacks better
        with self.conn as db:
            with db.cursor() as curs:
                result = curs.execute(statement, interp)

        return result

    def fetch_records(self, query, subs = ()):

        with self.conn as db:
            with db.cursor() as curs:
                curs.execute(query, subs)
                records = curs.fetchall()

        return records

    def fetch_one(self, query, subs = ()):

        with self.conn as db:
            with db.cursor() as curs:
                curs.execute(query, subs)
                record = curs.fetchone()

        return record
