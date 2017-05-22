import os
from application import create_app as create_app_base
import unittest
from flask.ext.sqlalchemy import sqlalchemy

from counter.models import Counter
from settings import DB_HOST
from application import db

class CounterTest(unittest.TestCase):
    def create_app(self):
        return create_app_base(
            SQLALCHEMY_DATABASE_URI=self.db_uri + '/' + self.db_name,
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY = 'mySecret!'
        )

    def setUp(self):
        # we need to use the root user
        # to be able to create the new database
        self.db_username = os.environ['DB_USERNAME']
        self.db_password = os.environ['DB_PASSWORD']
        self.db_name = os.environ['DATABASE_NAME'] + '_test'
        self.db_uri = 'postgresql://%s:%s@%s:5432' % (self.db_username, self.db_password, DB_HOST)
        engine = sqlalchemy.create_engine(self.db_uri + '/postgres')
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("create database "  + self.db_name)
        conn.close()
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()
        with self.app_factory.app_context():
            db.create_all()

    def tearDown(self):
        engine = sqlalchemy.create_engine(self.db_uri + '/postgres')
        conn = engine.connect()
        conn.execute("commit")
        # close all active connections
        conn.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'counter_test' AND pid <> pg_backend_pid()")
        conn.execute("commit")
        conn.execute("drop database "  + self.db_name)
        conn.close()

    def test_counter(self):
        rv = self.app.get('/')
        assert '1' in str(rv.data)
        rv = self.app.get('/')
        assert '2' in str(rv.data)
