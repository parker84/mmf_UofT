from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('Agg')
from plotnine import *
from scipy.cluster import hierarchy
import scipy.stats as stats
from sklearn.ensemble import RandomForestClassifier
from lib.python import os_helpers

import sys


def plot_feature_imps(imps, cols, savedir,save_plot=False,saveas=None, print_graph=False, top_n=None, fill=None, title='feature_imps'):
    feat_imp_df = pd.DataFrame([])
    feat_imp_df['importance'] = imps
    feat_imp_df['feature'] = cols
    feat_imp_df = feat_imp_df.sort_values(by=['importance'], ascending=False)
    if top_n is None:
        top_n = feat_imp_df.shape[0]
    feat_imp_df = feat_imp_df.iloc[:top_n]

    if fill is not None:
        fig = (ggplot(feat_imp_df,
                 aes(x='feature', y='importance', fill=fill)) +
                geom_bar(stat='identity') +
                ggtitle(title) +
                theme(axis_text_x=element_text(rotation=90, hjust=1)))
    else:
        fig = (ggplot(feat_imp_df,
                      aes(x='feature', y='importance')) +
               geom_bar(stat='identity') +
               ggtitle(title) +
               theme(axis_text_x=element_text(rotation=90, hjust=1)))
    if save_plot==True:
        os_helpers.check_if_dir_exists_if_not_make_it(savedir)
    if saveas is not None:
        fig.save(savedir+saveas)
    if print_graph:
        print(fig)


class SelFeats(object):

    def __init__(self, df, disc_cols, cts_cols, y_col, n_neighbours=None):
        """
        :param df:
        :param disc_cols:
            - these should be label encoded in df
        :param cts_cols:
        :param y_col:
        """
        self.df = df
        self.disc_cols = np.unique(disc_cols)
        self.cts_cols = np.unique(cts_cols)
        self.feats = np.unique(list(disc_cols) + list(cts_cols))
        self.y = df[y_col]
        self.n_neighbours = n_neighbours



    def get_feature_MI(self, plot=False):
        mi_df = pd.DataFrame([])
        is_discrete = [i in self.disc_cols for i in self.feats]
        mi_df['MI'] = mutual_info_classif(self.df[self.feats], self.y,
                                  random_state=RANDOM_SEED,
                                  n_neighbors=self.n_neighbours,
                                          discrete_features=is_discrete)
        mi_df['col_name'] = self.feats
        self.mi_df = mi_df.sort_values(by='MI', ascending=False)
        if plot == 'print':
            self.mi_df.iloc[:20].plot('col_name', 'MI', kind='bar',
                                      figsize=(20,10))
            plt.show()

            p = ggplot(mi_df, aes('MI')) +\
                geom_histogram(bins=60)
            print(p)
        self.feature_sel_criterion = self.mi_df
        self.feature_sel_criterion.index = self.mi_df.col_name
        assert self.mi_df.shape[0] == self.mi_df.col_name.unique().shape[0]


    def qa_selected_cols(self, cols):
        sel_cols_df = pd.DataFrame([])
        sel_cols_df['col_name'] = cols
        print('ivs for the columns considering: \n{}'.format(
            self.feature_sel_criterion.merge(sel_cols_df, how='inner', on=['col_name'])))

    def remove_related_features(self, contending_cols, sim_func, threshold):
        """
        start at the first col in contending_cols compare w rest of the columns
        and remove all cols below that are more similar than the threshold
        if the next feature wasnt removed repeat w that one
        ass:
        - self.feature_sel_criterion has been created
        :param contending_cols:
        :param sim_func: (x, y) -> float or tuple = similarity (higher => more sim)
            - if tuple 2nd val interpreted as pval
        :param threshold: if sim_func > thresh => drop this col
        :return:
        """
        contender_cols = contending_cols.copy()
        ix_upper = 0
        while ix_upper < len(contender_cols):
            upper_col = contender_cols[ix_upper]
            ix_upper += 1
            for ix_lower in range(1, len(contender_cols)):
                if ix_lower < len(contender_cols):
                    lower_col = contender_cols[ix_lower]
                    sim = sim_func(self.df[upper_col], self.df[lower_col])
                    if not isinstance(sim, float):
                        sim, pval = sim
                    else:
                        pval=' not relevant '
                    if sim > threshold:
                        print('removing column: {} due to a similarity of : {} and pval: {} w column: {}'.format(
                            lower_col, sim, pval, upper_col
                        ))
                        self.feature_sel_criterion.drop(lower_col, inplace=True)
                        contender_cols.pop(ix_lower)
        return contender_cols



    def remove_highly_correlated_cts_features(self, contending_cols, threshold=.95):
        cts_contenders = [c for c in contending_cols if c in self.cts_cols]
        cts_contenders = self.remove_related_features(cts_contenders, stats.pearsonr,
                                                      threshold=threshold)
        cts_contenders = cts_contenders + [c for c in contending_cols if c in self.disc_cols]
        assert len(cts_contenders) == len(np.unique(cts_contenders))
        return cts_contenders

    def remove_highly_related_disc_features(self, contending_cols, threshold):
        """
        This test is invalid when the observed or expected frequencies in each category
        are too small.
        A typical rule is that all of the observed and expected
        frequencies should be at least 5.
        :param contending_cols:
        :param threshold:
        :return:
        """
        # cts_contenders = [c for c in contending_cols if c in self.cts_cols]
        # self.remove_related_features(cts_contenders, np.correlate(), threshold=threshold)
        pass


    def make_mi_similarity_matrix(self, cols):
        """
        :param cols: cols you'd like to consider
        :return:
        """
        n_cols = len(cols)
        print('cols were aout to get MI matrix for: {}'.format(cols))
        mi_between_features = pd.DataFrame(np.zeros((n_cols, n_cols)))
        for i in range(n_cols):
            c = cols[i]
            print('getting MI for col: {}'.format(c))
            if c in self.disc_cols:
                mi_between_features['MI'] = mutual_info_classif(self.df[cols], self.df[c],
                                  random_state=RANDOM_SEED,
                                  n_neighbors=self.n_neighbours)
            elif c in self.cts_cols:
                mi_between_features['MI'] = mutual_info_regression(self.df[cols], self.df[c],
                                                                random_state=RANDOM_SEED,
                                                                n_neighbors=self.n_neighbours)
        self.feature_similarity_matrix = mi_between_features
        self.feature_similarity_matrix.index = cols
        self.cluster_cols = cols


    def hclust_feature_sim_matrix(self, method='single'):
        """
        see why single in the justifcations below
        :param method:
        :return:
        """
        self.linkage = hierarchy.linkage(self.feature_similarity_matrix, method=method)
        hierarchy.dendrogram(self.linkage) # can alter params to clean up: https://s3.amazonaws.com/assets.datacamp.com/production/course_3161/slides/ch2_slides.pdf
        plt.show()

    def assign_hclust_clusters(self, max_distance, max_clust=None):
        """
        assumes linkage is deinfed
        :param n_clusters:
        :return:
        """
        if max_clust is None:
            self.clusters = hierarchy.fcluster(self.linkage, max_distance, criterion='distance')
        else:
            self.clusters = hierarchy.fcluster(self.linkage, max_clust, criterion='maxclust')
        self.feature_similarity_matrix['clusters'] = self.clusters
        self.feature_similarity_matrix['cols'] = self.cluster_cols


    def select_top_cluster(self, feature_selection_criterion_col='MI'):
        """
        select the top feature according to our feature_selection_criterior_col in each cluster
        ass:
        - clusters have already eben assigned to self.feature_similarity_matrix
        :param n_neighbours:
        :param plot:
        :return:
        """
        sel_feats = self.feature_similarity_matrix.groupby('cluster').max(feature_selection_criterion_col)
        import pdb; pdb.set_trace()



    def heatmap_feature_sim_matrix(self, cols):
        """
        :param cols:
        :return:
        """
        plt.imshow(self.feature_similarity_matrix.loc[cols, cols])
        plt.show()


    def get_rf_feature_imps(self):
        rf = RandomForestClassifier()
        rf.fit(self.df[self.feats], self.y)
        feat_imps = rf.feature_importances_
        rf_imp_df = pd.DataFrame([])
        rf_imp_df['rf_importance'] = feat_imps
        rf_imp_df['col_name'] = self.feats
        rf_imp_df.sort_values(by='rf_importance', ascending=False, inplace=True)
        self.feature_sel_criterion = rf_imp_df
        self.feature_sel_criterion.index = rf_imp_df.col_name
        assert rf_imp_df.col_name.unique().shape[0] == rf_imp_df.shape[0]


"""
resources:
- hclust in python using a distance matrix: http://mdtraj.org/development/examples/clustering.html
- plotting dendrograms in python: https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/

justifications
- single linkage
    - because we want our clusters to be very different more than we care about them being similar
    - single will attach a point into a cluster based on this most similar point
    - thus if we 2 different clusters this should be becuase no points in either cluster should be overly similar

"""