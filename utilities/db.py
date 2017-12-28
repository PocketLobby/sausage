import psycopg2
from utilities.configurator import Configurator

class DB:
    """Holds a connection to the database"""
    config = Configurator().config

    cur = None

    def db_cur(self):
        "Memoize a connection cursor"
        return self.cur if self.cur else self._assign_conn_cur()

    def execute(self, statement):
        """Execute and commit a db statement"""
        self.db_cur().execute(statement)
        return self.conn.commit()

    def fetch_records(self, query, subs = ()):
        self.db_cur().execute(query, subs)
        records = self.db_cur().fetchall()
        return records

    def _assign_conn_cur(self):
        self.cur = self.conn.cursor()
        return self.cur

    @property
    def conn(self):
        """Sets up a connection to the database"""

        # NOTE: I have yet to have a good reason to test that the db works
        if self.config['ENV'] == 'test':
            raise NotImplementedError("don't use the db in test")

        return psycopg2.connect(host=self.config['db_host'],
                user=self.config['db_user'],
                database=self.config['db_db'])
