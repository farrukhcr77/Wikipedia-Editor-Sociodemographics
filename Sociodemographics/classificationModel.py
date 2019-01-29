from __future__ import  division
from sklearn import svm
from sklearn import linear_model
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score

class ClassificationModel():

    def __init__(self, features, iterations):
        self.features = features
        self.iterations = iterations


    def evaluate_models(self):

        # Init mean scores
        score_svc_linear_mean  = 0
        score_svc_default_mean = 0
        score_logReg_mean      = 0

        for iteration in range(0, self.iterations):

            # Data is shuffled every call on get_train_test_data()
            train_x, train_y, test_x, test_y = self.features.get_train_test_data()

            # SVM with linear kernel
            svc_clf = svm.SVC(kernel='linear')
            svc_clf.fit(train_x, train_y)
            predict_svc_linear = svc_clf.predict(test_x)
            score_svm_linear   = accuracy_score(test_y, predict_svc_linear)

            # SVM with rbf kernel
            svc_clf_rbf = svm.SVC(kernel='rbf')
            svc_clf_rbf.fit(train_x, train_y)
            predict_svc_rbf = svc_clf_rbf.predict(test_x)
            score_svm_rbf = accuracy_score(test_y, predict_svc_rbf)

            param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000] }
            logReg_clf = GridSearchCV(linear_model.LogisticRegression(penalty='l2'), param_grid)
            logReg_clf.fit(train_x, train_y)
            predict_logReg = logReg_clf.predict(test_x)
            score_logReg = accuracy_score(test_y, predict_logReg)



            score_svc_linear_mean  +=   score_svm_linear
            score_svc_default_mean +=   score_svm_rbf
            score_logReg_mean      +=   score_logReg


        # Print scores
        print ("Evaulation scores using accuracy_score")
        print ("SVM with linear kernel               : ", score_svc_linear_mean/self.iterations)
        print ("SVM with rbf kernel                  : ", score_svc_default_mean/self.iterations)
        print ("Linear regression                    : ", score_logReg_mean/self.iterations)