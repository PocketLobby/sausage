import psycopg2
from utilities.configurator import Configurator

class DB:
    """Holds a connection to the database"""
    config = Configurator().config

    conn = psycopg2.connect(host=config['db_host'],
                            user=config['db_user'],
                            database=config['db_db'])

    cur = None

    def db_cur(self):
        "Memoize a connection cursor"
        return self.cur if self.cur else self._assign_conn_cur()

    def fetch_records(self, query, subs = ()):
        self.db_cur().execute(query, subs)
        records = self.db_cur().fetchall()
        return records

    def _assign_conn_cur(self):
        self.cur = self.conn.cursor()
        return self.cur
