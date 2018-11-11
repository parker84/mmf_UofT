"""
module for reading and writing to different databases
"""

import pandas as pd
# import pypyodbc
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pymysql
import psycopg2
from settings import *

pymysql.install_as_MySQLdb()
import MySQLdb

HOST = 'localhost'
CHARSET = 'utf8'
USER = 'Brydon'
PASSWD = 'mysql_root2456'
# DB = 'fin_project'
SERVER = 'THE-ENTERPRISE\SQLEXPRESS'




class ReadWriteData(object):

    def __init__(self, table_name=None, db=DB, host=PSQL_HOST, user=PSQL_USER,
                 passwd=PSQL_PWD,
                 port=PSQL_PORT,
                 raw_rows=None, server=SERVER,
                 charset=CHARSET,
                 df=None):

        self.table_name = table_name
        self.raw_rows = raw_rows
        self.charset = charset
        self.database = db
        self.host = host
        self.user = user
        self.port = port
        self.passwd = passwd
        self.raw_rows = raw_rows
        self.server = server
        if df is not None:
            self.df = df
        self.mysql_engine = None
        self.conn = None
        self.psql_engine = None

    # def check_sql_ready(self):
    #     """
    #     check whether we have all the required inputs to query from mysql
    #     :return:
    #     """
    #     assert self.server is not None and self.database is not None , \
    #         'one of the following is none: {}'.format(', '.join([self.server, self.database]))
    #
    # def make_sql_conn(self):
    #     self.check_sql_ready()
    #     if self.sql_conn is not None:
    #         self.sql_conn = pypyodbc.connect(
    #             'driver={SQL Server};server={};database={};trusted_connection=true'.format(self.server, self.database))
    #
    # def get_df_from_sql(self):
    #
    #     self.make_sql_conn()
    #     if self.raw_rows is not None:
    #         df = pd.read_sql('select top {} * from {}'.format(self.raw_rows, self.table_name), self.sql_conn)
    #     else:
    #         df = pd.read_sql('select * from {}'.format(self.table_name), self.sql_conn)
    #     print(df.head())
    #     self.df = df
    #
    # def save_to_sql(self, tblname):
    #     print('saving to sql')
    #     self.make_sql_conn()
    #     self.df.to_sql(tblname, self.sql_conn)

    def check_mysql_ready(self):
        """
        check whether we have all the required inputs to query from mysql
        :return:
        """
        assert self.user is not None and self.passwd is not None and self.host is not None and self.database is not None, \
            'one of the following is none: {}'.format(', '.join([self.user, self.passwd, self.host, self.database]))

    def make_mysql_engine(self):
        self.check_mysql_ready()
        if self.mysql_engine is None:
            self.mysql_engine = create_engine("mysql+mysqldb://{}:{}@{}:3306/{}?charset={}".format(
                self.user, self.passwd, self.host, self.database, self.charset))
        else:
            print('self.mysql_engine already exists using that one')

    def pd_to_mysql(self, df=None, if_exists='replace', table=None):
        """
        take df and send it into mysql at the table and db specified
        :param table: tblname
        :param df:
        :param if_exists: ['replace', 'append', 'ignore]
        :param db1:
        :return:
        """
        self.make_mysql_engine()
        if df is None:
            df = self.df
        if table is None:
            table = self.table_name
        df.to_sql(table, self.mysql_engine,
                  if_exists=if_exists)
        return 'df saved at :{}'.format(table)

    def query_mysql_table(self, query):
        """here we extract a table from our db and df it
        ass if youre making the query you;ll set you're own limit
        """
        self.make_mysql_engine()
        try:
            df = pd.read_sql(query, con=self.mysql_engine)
            return df
        except Exception as error:
            print('error that occured: {}'.format(error))

    def save_to_sqlite(self, tblname):
        conn = sqlite3.connect("WideWorldImporters.db")
        self.df.to_sql(tblname, conn)

    # def psql_connect(self, database_name, host=PSQL_HOST,
    #                  user=PSQL_USER, password=PSQL_PASSWD):
    #     params = "dbname = %s user = %s host = %s password = %s" % \
    #              (database_name, user, host, password)
    #     try:
    #         print ('Connecting to the PSQL database...')
    #         self.conn = psycopg2.connect(params)
    #         print ('Connection successful.')
    #         return self.conn
    #     except (Exception, psycopg2.DatabaseError) as error:
    #         print (error)

    def make_psql_engine(self):
        if self.psql_engine is None:
            # self.psql_engine = create_engine("postgresql://{}:{}@{}:5432/{}?charset={}".format(
            #     user, password, host, database_name, self.charset))
            # self.psql_engine = create_engine("postgresql://{}:{}@{}:5432/{}".format(
            # self.psql_engine = create_engine("192.168.65.2://{}:{}@{}:5432/{}".format(
            # self.psql_engine = create_engine("http://docker.for.mac.localhost://{}:{}@{}:5432/{}".format(
            if self.port is None:
                port = 5432
            else:
                port = self.port
            self.psql_engine = create_engine("postgresql://{}:{}@{}:{}/{}".format(
                self.user, self.passwd, self.host, port, self.database))
        # else:
        #     print('self.mysql_engine already exists using that one')

    def pd_to_psql(self, df=None, if_exists='replace', table=None):
        """
        take df and send it into psql at the table and db specified
        :param table: tblname
        :param df:
        :param if_exists: ['replace', 'append', 'ignore]
        :param db1:
        :return:
        """
        self.make_psql_engine()
        if df is None:
            df = self.df
        if table is None:
            table = self.table_name
        df.to_sql(table, self.psql_engine,
                  if_exists=if_exists)
        return 'df saved at :{}'.format(table)

    def query_psql_table(self, query):
        """
        :param query:
        :param dbname:
        :return:
        """
        self.make_psql_engine()
        df = pd.read_sql_query(query, con=self.psql_engine)
        return df

    def execute_psql_table(self, query):
        self.make_psql_engine()
        execute_query = text(query)
        self.psql_engine.execution_options(autocommit=True).execute(execute_query)

    def random_sample_psql_table(self, table, nrows):
        query = f"""
            select * from {table}
            order by random()
            limit {nrows}
        """
        return self.query_psql_table(query)

    def sample_labels_from_psql_for_one_class(self, y_col, table, nrows):
        query = f"""
            select *, distinct on ({y_col})
            from {table}
            where {y_col} = 1
            order by rand()
            limit {nrows}
        """

        return self.query_psql_table(query)

    def make_and_fill_psql_column_with_constant(self, constant, dtype, col, table):
        self.make_mysql_engine()
        try:
            self.query_psql_table(f"""
                alter table {table} add "{col}" {dtype}
            """)
            # TODO: can but default val on col creation
            self.query_psql_table(f"""
                insert into {table} ("{col}") select {constant} from {table}
            """)
        except Exception as error:
            print(error)


