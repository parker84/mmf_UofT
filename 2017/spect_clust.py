import numpy as np


def get_distance_matrix(df, distance_measure, feat_col_ix=1):
    """
    return a distance matrix between every row of df

    Note: could probably be made faster w matrix algebra

    ass:
    - each row of df is an observation
    - distance measure returns 2 vals, 1st is of interest

    :param df:
    :param distance_measure:
    :param feat_col_ix: all cols > this val are used in distance computation
    :return:
    """
    n = len(df)
    dist_matrix = np.zeros((n,n))
    for i in range(n):
        for j in range(j):
            si = df.iloc[i, feat_col_ix:]
            sj = df.iloc[j, feat_col_ix:]
            dist_matrix[i,j] = distance_measure(si, sj)[0]
    return dist_matrix

def spect_embed(A, normed=True):
    D = np.diag(A.sum(axis=0))
    L = D - A
    if normed:
        Dsqrt = np.diag(1/np.sqrt(A.sum(axis=0)))
        Ln = np.dot(np.dot(Dsqrt, L), Dsqrt)
    else:
        Ln=L
    lams, eigs = np.linalg.eig(Ln)
    plt.plot(range(len(lams), sorted(lams)))
    return eigs, lams


class spectral_FE(object):
    """
    return features derived from specrtal clusters
    """

    def __init__(self, ret_df, clusts, dep='daily1_rets', n=1):
        """
        :param ret_df:
        :param clusts: df w ticker and clust cols
        """
        self.df = ret_df
        self.dep = dep
        self.n = n
        self.df = self.df.merge(clusts[['ticker', 'clust']],
                                how='inner', on=['ticker'])
        self.get_daynums()
        self.join_ndays_ago_on()
        self.get_clust_feats()

    def get_daynums(self):
        """
        add daynums to self
        :return:
        """
        self.df = self.df.sort_values(by=['ticker', 'date'])
        daynum = 0
        daynums = []
        tick = None
        for i in self.df.index:
            daynums.append(daynum)
            if tick is not None:
                if self.df.ticker.loc[i] == tick:
                    daynum += 1
                else:
                    daynum = 0
            tick = self.df.ticker.loc[i]
        self.df['daynum'] = daynums
        print('head check daynums: {} \n\n'.format(self.df[['daynum', 'ticker', 'date']].head()))

    def join_ndays_ago_on(self):
        """
        join on dep for n days ago
        :return:
        """
        n = self.n
        daynumpn = 'daynum_p{}'.format(n)
        self.df[daynumpn] = self.df.daynum + n
        print('shape before join: {}'.format(self.df.shape))
        self.df = self.df.merge(
            self.df[['ticker', self.dep, daynumpn, 'daynum']],
            how='inner',
            left_on=['ticker', daynumpn],
            right_on=['ticker', 'daynum'],
            suffixes=['', '_{}_days_ago'.format(n)]
        )
        print('shape after join: {}'.format(self.df.shape))
        print(self.df.head())

    def get_clust_feats(self, funcs=[np.mean, np.std, np.median, max, min]):
        col = '{}_{}_days_ago'.format(self.dep, self.n)
        clusts = self.df.groupby(['clust'])[col].aggregate(funcs).reset_index()
        print(clusts.head())
        # [self.dep].aggregate(funcs).reset_index()
        self.df = self.df.merge(clusts, on='clust', how='inner')


