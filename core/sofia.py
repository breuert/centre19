import subprocess
import re

import numpy as np

from sklearn.datasets import dump_svmlight_file, load_svmlight_file


class Logreg():
    '''
    This class is in a very experimental state. In order to use it sofia-ml needs to be downloaded, compiled
    and the respective path is accessible.
    '''
    def __init__(self, n_feat, sofia_ml):
        self.n_feat = n_feat
        self.sofia_ml = sofia_ml

    def predict_proba(self, feat):
        '''
        ./sofia-ml --test_file dummy.test --dimensionality 657414 --model_in model --results_file results
        '''

        tfidf_file = 'tfidf_feat_tmp'
        dump_svmlight_file(feat, np.array([0]), tfidf_file, multilabel=False, zero_based=False)
        process = self.sofia_ml + ' --test_file ' + tfidf_file + ' --dimensionality ' + \
                  str(self.n_feat) + ' --model_in model --results_file result'
        output = subprocess.run([process], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = open('result')
        text = result.read()
        result_text = re.split(r'\t+', text)

        proba = result_text[0]

        return [[0, proba]]

    def fit(self, train_data):
        '''
        ./sofia-ml --learner_type logreg-pegasos --loop_type stochastic --lambda 0.1  --training_file dummy.train --dimensionality 657414 --model_out model
        '''

        x_train, y_train = load_svmlight_file(train_data, n_features=self.n_feat)

        for i in range(0,len(y_train)):
            if y_train[i] == 0:
                y_train[i] = -1

        train_data_sofia = 'train_data_sofia'

        dump_svmlight_file(x_train, y_train, train_data_sofia, multilabel=False, zero_based=False)

        process = self.sofia_ml + ' --learner_type logreg-pegasos --training_file ' + \
                  train_data_sofia + ' --dimensionality ' + str(self.n_feat) + ' --model_out model'
        output = subprocess.run([process], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
