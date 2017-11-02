"""
Note:
    - we dont filter beforehand, because after filtering we only lose a small percentage of rows, but often this is not the case
        like in deriving associations things really blow up so make sure you filter before you start the Feature eng not inside it
"""


import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import pypyodbc
from datetime import datetime, timedelta
import sqlite3


def count_gt_25g(L, n=2500):
    """
    count the number of elements in L > n
    :param L:
    :param n:
    :return:
    """
    return sum(np.array(L) > n)

def count_gt_1g(L, n=1000):
    """
    count the number of elements in L > n
    :param L:
    :param n:
    :return:
    """
    return sum(np.array(L) > n)

def count_gt_5g(L, n=5000):
    """
    count the number of elements in L > n
    :param L:
    :param n:
    :return:
    """
    return sum(np.array(L) > n)

def dt_str(d):
    return datetime.strptime(d, '%Y-%m-%d')

class FE_df(object):

    def __init__(self, dfname, feat_names, primary_key='orderlineid',
            dependent='total_rev', day_col='orderdate',
                 funcs=[np.mean, np.median, len, count_gt_1g, count_gt_5g, count_gt_25g], raw_rows=None,
                 days_back=30, min_num_per_feat=5):
        """
        Notes
        - youll get an error if your dates dont line up (should fix this)
        :param dfname:
        :param feat_names:
        :param primary_key:
        :param dependent:
        :param day_col:
        :param funcs:
        :param raw_rows:
        :param days_back:
        """
        self.min_num_per_feat = min_num_per_feat
        self.dfname = dfname
        self.dep = dependent
        self.raw_rows = raw_rows
        self.feat_names = feat_names
        self.primary_key=primary_key
        self.day_col = day_col
        self.funcs = funcs
        self.rawdf = self.get_df_from_sql()[feat_names + [dependent, day_col, primary_key]]
        print('rawdf columns: {}'.format(self.rawdf.columns))
        self.rawdf[day_col] = [dt_str(i) for i in self.rawdf[self.day_col]]
        self.df = self.get_feats_allt(days_back)
        # in the future one can adjust the days back to give more features
        print('shape of self.df: {} \n\n shape of raw df: {}'.format(self.df.shape, self.rawdf.shape))


    def get_df_from_sql(self):
        # engine2 = create_engine('sql://')
        # connection2 = engine2.connect()
        conn = pypyodbc.connect('driver={SQL Server};server=THE-ENTERPRISE\SQLEXPRESS;database=WideWorldImporters;trusted_connection=true')
        if self.raw_rows is not None:
            df = pd.read_sql('select top {} * from {}'.format(self.raw_rows, self.dfname), conn)
        else:
            df = pd.read_sql('select * from {}'.format(self.dfname), conn)
        print(df.head())
        return df

    def get_feats_at_t(self, dft, col, t2):
        """
        - for all the self.dep in dft where col == colvals
            apply our functions
        - colvals = the values that occur for our col at time t==t2
        - isolcated to a specific col
        :param col: column were grouping by (Consumer or productid,...)
        :param t2: the final day date being used, we use this to derive the colvals
        :return: dataframe consisting of our funcs applied on the dep on dft for each relevant
            group of col
        """
        print('\n applying a specific feature {} on time: {}'.format(col, t2))
        #dft2 = dft[dft[self.day_col] == t2]
        # in creation of dft we only considered day cols < t2
        dft2 = self.rawdf[self.rawdf[self.day_col] == t2]
        #print(dft[self.day_col].iloc[0], t2)
        colvals = dft2[col].unique()
        print('number of unique colvals: {} for the column: {}'.format(len(colvals), col))
        dft['has_colval'] = [i in colvals for i in dft[col]]
        print('number of rows in dft with one of our colvals: {}'.format(sum(dft.has_colval)))
        dff = dft[dft.has_colval]
        print('shape of our filtered dft (data frame for our feature range) with a colval of interest at time t2: {}'.format(dff.shape))
        dfa = dff.groupby(col)[self.dep].aggregate(self.funcs).reset_index()
        print('columns of our aggd groupby (dfa) pre filtering {}, shape of the aggd groupby: {}'.format(dfa.columns, dfa.shape))
        dfa = dfa[dfa.len > self.min_num_per_feat]
        print('shape of our aggd df {} after filtering our for the minimum number of transactions per features: {}'.format(
            dfa.shape, self.min_num_per_feat))
        #dfa.columns[len(self.funcs) - 1:] = ['{}_{}'.format(col, i) for i in
        #dfa.columns = (list(dfa.columns[:(len(self.funcs)-1)]) +
        dfa.columns = (list(dfa.columns[:-(len(self.funcs))]) +
                       ['{}_{}'.format(col, i) for i in
                                             dfa.columns[-(len(self.funcs)):]])
        # print(dfa.head())
        # print(dft2.head())
        dfw = dfa.merge(dft2, on=col, how='left')
        print('columns of df for this feature at t2 after merge with dft {}'.format(dfw.columns))
        print('shape of our features: {} from time: {}, where we merge on the features in or feature range onto to right rows at time \n'.format(
            dfw.shape, t2
        ))
        return dfw

    def get_all_feats_at_t(self, dft, t2):
        """
        return all features from dft on our dep across the columns were interested in
        :param dft:
        :return:
        """
        print('\n\n\n\n getting all features at time {} \n'.format(t2))
        df = self.get_feats_at_t(dft, self.feat_names[0], t2)
        for col in self.feat_names[1:]:
            #dft = self.get_feats_at_t(dft, col, t2)
            # we were overwriting the variable input (it was late :))
            df_col_feats = self.get_feats_at_t(dft, col, t2)
            df = df.merge(df_col_feats, how='left', on=([self.primary_key, self.dep, self.day_col] + list(self.feat_names)))
        df.index = range(len(df))
        print('shape of dft (rawdf w dates between t1 and t2 below) {} \n shape of our feature df (df) from this t2 {} after getting the feats for columns: {} \n\n\n\n'.format(
            dft.shape, df.shape, self.feat_names
        ))
        return df

    def get_dft(self, t2, days_back):
        """
        return filtered version of rawdf in date range
        :param t2:
        :param days_back:
        :return:
        """
        #print(t2)
        t1 = t2.astype('M8[ms]').astype('O')  - timedelta(days=days_back)
        #return self.rawdf.query('{} < {} and {} >= {}'.format(self.day_col, t2, self.day_col, t1))
        #print(self.rawdf[self.day_col])
        #print(t1, t2)
        dft = self.rawdf[self.rawdf[self.day_col] < t2][self.rawdf[self.day_col] >= t1]
        print('shape of dft: {}'.format(dft.shape))
        return dft

    def get_feats_allt(self, days_back):
        """
        derive features for every day based on days_back days back
        :return: features
        """
        unq_dates = sorted(self.rawdf[self.day_col].unique())
        num_dates = len(unq_dates)
        print('max date: {}, min date: {}, num dates: {}'.format(max(unq_dates), min(unq_dates), num_dates))
        t2 = unq_dates[days_back-1]
        df = self.get_all_feats_at_t(self.get_dft(t2, days_back), t2)
        i=0
        for t2 in unq_dates:
            print('-------------- iter {} out of {}'.format(i, num_dates))
            print('-------------- date {}'.format(t2))
            i+=1
            dft = self.get_dft(t2, days_back)
            #print(dft.head())
            if dft.shape[0] > 0:
                dft = self.get_all_feats_at_t(dft, t2)
                df = df.append(dft)
                # print(dft.head())
                # print(df.head())
                print('shape of df: {} = appended features over each time period'.format(df.shape))
            else:
                print('skipped dt: {} because len of dft (rawdf filtered for our feature period) == 0'.format(t2))
        df.index = range(len(df))
        print('head of final features: {} \n\n tail of final features: {}'.format(df.head(), df.tail()))
        return df

    def save_to_sql(self, tblname):
        print('saving to sql')
        conn = pypyodbc.connect(
            'driver={SQL Server};server=THE-ENTERPRISE\SQLEXPRESS;database=WideWorldImporters;trusted_connection=true')
        self.df.to_sql('features_by_product_lifespan', conn)

    def save_to_sqlite(self, tblname):
        conn = sqlite3.connect("WideWorldImporters.db")
        self.df.to_sql(tblname, conn)



if __name__ == '__main__':
    fe = FE_df('feature_table_per_order', feat_names=['customerid', 'stockitemid'], primary_key='orderlineid',
            dependent='total_rev', day_col='orderdate',
               funcs=[np.mean, np.median, len, count_gt_1g, count_gt_5g, count_gt_25g], raw_rows=None, days_back=300, min_num_per_feat=5)
    fe.df.to_csv('features_from_python_gs.csv')
    #fe.save_to_sql('test')ß
    #fe.save_to_sqlite('temp2')



