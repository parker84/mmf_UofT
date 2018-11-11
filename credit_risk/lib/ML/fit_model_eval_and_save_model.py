import numpy as np
from sklearn.linear_model import LogisticRegression
import sys
import pandas as pd
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
from plotnine import *
from lib.ML.eval import EvalBinaryClassifier
#from prep import one_hot
from sklearn.model_selection import KFold, TimeSeriesSplit, GroupKFold, GridSearchCV
from sklearn.externals import joblib
from lib.python import date_helpers
from settings import *
from lib.python import os_helpers
from sklearn import metrics


class FitEvalSaveModel(object):

    def __init__(self, dfs, feat_names, dep_names):
        self.dfs = dfs
        self.feat_names = feat_names
        self.y_cols = dep_names
        for name in self.dfs:
            self.dfs[name]['Tag'] = name


    def fit_model_add_probs(self, model):
        self.model = model.fit(self.dfs['train'][self.feat_names], self.dfs['train'][self.y_cols])
        for name in self.dfs:
            probs = self.model.predict_proba(self.dfs[name][self.feat_names])
            prob_df = pd.DataFrame(probs, columns=['probs{}' for i in range(probs.shape[1])])
            self.dfs[name].index = range(self.dfs[name].shape[0])
            self.dfs[name] = self.dfs[name].join(prob_df)

    def fit_model_add_preds(self, model):
        self.model = model.fit(self.dfs['train'][self.feat_names], self.dfs['train'][self.y_cols])
        for name in self.dfs:
            probs = self.model.predict(self.dfs[name][self.feat_names])
            prob_df = pd.DataFrame(probs, columns=['preds{}'.format(i) for i in range(probs.shape[1])])
            self.dfs[name].index = range(self.dfs[name].shape[0])
            self.dfs[name] = self.dfs[name].join(prob_df)

    def cross_validate_train(self, model, eval_func, nfolds=3, fold_func=KFold):
        """
        :param models:
        :param eval_func: (model, X, y) -> evalling shit
        :param fold_func: usually one of: KFold, TimeSeriesSplit, GroupKFold
        :return:
        """
        kf = fold_func(nfolds)
        i=0
        data = self.dfs['train']
        for train_ix, test_ix in kf.split(data):
            fold_model = model
            Xtrain, ytrain = data.iloc[train_ix][self.feat_names], data.iloc[train_ix][self.y_cols]
            fold_model.fit(Xtrain, ytrain)
            Xtest, ytest = data.iloc[test_ix][self.feat_names], data.iloc[test_ix][self.y_cols]
            print('training')
            eval_func(fold_model, Xtrain, ytrain, '{}_training'.format(i))
            print('testomg')
            eval_func(fold_model, Xtest, ytest, '{}_testing'.format(i))
            i+=1


    def eval_binary_mod(self, save_images_path):
        """
        datasets should have a prob0 and prob1 col before running this
        :return:
        """
        for name in self.dfs:
            EvalBinaryClassifier(self.dfs[name]['probs1'], self.dfs[name][self.y_cols],
                 show_plots=False,
                 save_plots=save_images_path + '_{}.png'.format(name))

    def save_results(self, save_preds_path):
        self.output_df = self.dfs['train']
        for name in ['test', 'hold']:
            self.output_df = self.output_df.append(self.dfs[name])
        self.output_df.to_csv(save_preds_path)