"""
resources:
- lift: https://heuristically.wordpress.com/2009/12/18/plot-roc-curve-lift-chart-random-forest/
    - https://cran.r-project.org/web/packages/ROCR/ROCR.pdf
- roc: http://blog.yhat.com/posts/roc-curves.html
- available metrics: http://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics
"""

from sklearn import metrics
import matplotlib
matplotlib.use('Agg')
from plotnine import *
import pandas as pd
import numpy as np
import sys
from lib.python import os_helpers
from lib.python import date_helpers


def get_eval_start_row(n_rows, n_labels_in_rows, n_labels_desired_in_eval):
    """
    get the starting row for the desired numbner of labels
    :param n_rows:
    :param n_labels_in_rows:
    :param n_labels_desired_in_eval:
    :return:
    """
    prob_label_per_row = n_labels_in_rows / n_rows
    req_rows = n_labels_desired_in_eval // prob_label_per_row
    start_eval_row = n_rows - req_rows
    print('req rows: {}, start eval row: {}'.format(req_rows, start_eval_row))
    print('E(number of labels in val set) = {}'.format(prob_label_per_row * req_rows))
    return start_eval_row

class EvalBinaryClassifier(object):


    def __init__(self, y_probs, y_true, show_plots=True,
                 save_plots=False,
                 prob_cutoff=.5,
                 print_probs_split_by_target=False):
        self.y_pred = y_probs > prob_cutoff
        self.y_probs = y_probs
        self.y_true = y_true
        self.acc = sum(self.y_pred == self.y_true) / len(y_true)
        self.save_image_dir = save_plots
        self.show_plots = show_plots
        self.save_plots = save_plots != False


        print('confusion matrix {}'.format(metrics.confusion_matrix(self.y_pred, y_true)))
        print('C_i,j = number of observations known to be in group i, but predicted to j')
        try:
            self.auc = metrics.roc_auc_score(self.y_true, self.y_probs)
            print('auc = {}, acc = {}'.format(self.auc, self.acc))
            print('auc score')
            if show_plots or save_plots:
                if save_plots:
                    print('saving plots to : {}'.format(self.save_image_dir))
                self.roc()
                self.lift()
                self.prec_recall()
                if print_probs_split_by_target:
                    self.plot_probs_split_by_target()
        except Exception as error:
            print('error: {}'.format(error))

    def roc(self):
        fpr, tpr, thresh_holds = metrics.roc_curve(self.y_true, self.y_probs)
        self.df_roc = pd.DataFrame(dict(fpr=fpr, tpr=tpr, thresh_holds=thresh_holds))
        g = ggplot(self.df_roc, aes('fpr', 'tpr')) + \
            geom_line() + \
            geom_abline(linetype='dashed') + \
            ggtitle('auc = {}'.format(self.auc))
        #print(g)
        #ggsave(g, self.save_image_dir + '_roc_{}'.format(date_helpers.get_datetime_now_in_str()))
        if self.show_plots:
            print(g)
        if self.save_plots:
            os_helpers.check_if_dir_exists_if_not_make_it(self.save_image_dir + 'roc/')
            g.save(self.save_image_dir + 'roc/_roc_{}.png'.format(date_helpers.get_datetime_now_in_str()))

    def lift(self):
        """
        have to call roc first
        :return:
        """
        self.df = pd.DataFrame([])
        self.df['preds'] = self.y_pred
        self.df['probs'] = self.y_probs
        self.df.sort_values(by='probs', inplace=True,
                            ascending=False)
        df = self.df.merge(self.df_roc, left_on='probs',
                      right_on='thresh_holds', how='left')
        assert len(df) == len(self.df)
        df['row_num'] = np.arange(0,len(df)) + 1
        df['rpp'] = df.row_num / len(df)
        df.dropna(axis=0, inplace=True) # dropping rows w matching TPR
        #assert df.shape[0] == self.df_roc.shape[0]-1
        g = ggplot(df, aes('rpp', 'tpr')) + \
            geom_line() +\
            ggtitle('lift_curve') +\
            geom_abline(linetype='dashed')
        if self.show_plots:
            print(g)
        if self.save_plots:
            os_helpers.check_if_dir_exists_if_not_make_it(self.save_image_dir + 'lift/')
            g.save(self.save_image_dir + 'lift/_lift_{}.png'.format(date_helpers.get_datetime_now_in_str()))

    def prec_recall(self):
        prec, recall, _ = metrics.precision_recall_curve(
            self.y_true, self.y_probs)
        dfpr = pd.DataFrame(dict(recall=recall, prec=prec))
        g = ggplot(dfpr, aes('prec', 'recall')) +\
            geom_line()
        if self.show_plots:
            print(g)
        if self.save_plots:
            os_helpers.check_if_dir_exists_if_not_make_it(self.save_image_dir + 'prec_recall/')
            g.save(self.save_image_dir + 'prec_recall/_prec_recall_{}.png'.format(date_helpers.get_datetime_now_in_str()))

    def plot_probs_split_by_target(self, bin_width=.01, y_min=0, y_max=100):
        self.df['y_true'] = self.y_true
        p = ggplot(self.df, aes('probs', color='factor(y_true)')) +\
            geom_density(aes(y='{} * ..count..'.format(bin_width)), alpha=.6) + \
            geom_histogram(binwidth=bin_width) +\
            ylim(y_min, y_max)
            #geom_density(stat='identity')
        # geom_histogram(bins=500) +\
        #geom_histogram()
        if self.save_plots:
            os_helpers.check_if_dir_exists_if_not_make_it(self.save_image_dir + 'probs_split/')
            p.save(self.save_image_dir + '_probs_split_by_target_{}.png'.format(date_helpers.get_datetime_now_in_str()))




class EvalMulticlassIndependentClassifier(object):
    """
    independent => not mutually exclusive
    """

    def __init__(self, y_probs, y_trues, show_plots=True,
                 save_plots=False,
                 prob_cutoff=.5,
                 print_probs_split_by_target=False):

        self.save_plots = save_plots

        i = 0
        for label in y_trues.columns:
            save_dir = self.get_save_dir_for_label(label)
            try:
                y_prob = pd.DataFrame(y_probs).iloc[:,i]
            except Exception as error:
                print(error)
                import pdb; pdb.set_trace()
            y_true = y_trues[label]
            EvalBinaryClassifier(y_prob, y_true, show_plots=show_plots,
                 save_plots=save_dir,
                 prob_cutoff=prob_cutoff,
                 print_probs_split_by_target=print_probs_split_by_target)
            i+=1

    def get_save_dir_for_label(self, label):
        save_dir = '{}/label_{}'.format(self.save_plots, label)
        save_dir = os_helpers.check_if_dir_exists_if_not_make_it(save_dir)
        return save_dir


if __name__ == '__main__':
    import numpy as np
    df = pd.DataFrame(dict(probs=np.random.random(100),
                           y=np.random.choice([0,1],100)))
    EvalBinaryClassifier(df.probs, df.y, show_plots=True,
                 save_plots='./test_plots',
                 prob_cutoff=.5)
