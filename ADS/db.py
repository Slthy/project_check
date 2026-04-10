import os
import pymysql
from dbutils.pooled_db import PooledDB
from flask import g

_pool = None


# Initialize and return the shared connection pool.
def _get_pool():
    global _pool
    if _pool is None:
        _pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=2,
            blocking=True,
            host=os.environ['MYSQL_HOST'],
            port=int(os.environ.get('MYSQL_PORT', 3306)),
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASSWORD'],
            database=os.environ['MYSQL_DATABASE'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    return _pool


# Wraps a pooled connection with execute, commit, rollback, and close helpers.
class MySQLDB:
    def __init__(self):
        self.conn = _get_pool().connection()

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        return cursor

    def executemany(self, query, params):
        cursor = self.conn.cursor()
        cursor.executemany(query, params)
        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


# Return the single connection for this request, creating it if needed.
def get_db():
    if 'db' not in g:
        g.db = MySQLDB()
    return g.db
