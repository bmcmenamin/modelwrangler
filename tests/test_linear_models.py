"""End to end testing on simple models
"""

# pylint: disable=C0103
# pylint: disable=C0325
# pylint: disable=E1101


import numpy as np
from scipy.stats import zscore

from sklearn.linear_model import LogisticRegression as sk_LogisticRegression
from sklearn.linear_model import LinearRegression as sk_LinearRegression

from model_wrangler.model_wrangler import ModelWrangler
from model_wrangler.dataset_managers import DatasetManager

from model_wrangler.model.corral.linear_regression import LinearRegressionModel
from model_wrangler.model.corral.logistic_regression import LogisticRegressionModel

from model_wrangler.model.tester import ModelTester


def make_linear_reg_testdata(in_dim=2, n_samp=1000):
    """Make sample data for linear regression
    """
    signal = zscore(np.random.randn(n_samp, 1), axis=0)

    X = zscore(np.random.randn(n_samp, in_dim), axis=0)
    X += 0.2 * signal
    X = zscore(X, axis=0)
    y = signal + 100
    return X, y

def make_linear_cls_testdata(in_dim=2, n_samp=1000):
    """Make sample data for linear regression
    """
    signal = zscore(np.random.randn(n_samp, 1), axis=0)
    X = zscore(np.random.randn(n_samp, in_dim), axis=0)
    X += 0.2 * signal
    X = zscore(X, axis=0)
    y = (signal > 0).astype(int)
    return X, y


def compare_scikt_and_tf(sk_model, tf_model, X, y, sk_params={}):

    sk_model = sk_model.fit(X, y.ravel())
    print('Scikit values:')
    print('\t coef: {}'.format(sk_model.coef_.ravel()))
    print('\t int: {}'.format(sk_model.intercept_.ravel()))

    dm = DatasetManager([X], [y])
    tf_model.add_data(dm, dm)

    print('TF training:')
    print('\tpre-score: {}'.format(tf_model.score([X], [y])))
    tf_model.train()
    print('\tpost-score: {}'.format(tf_model.score([X], [y])))

    print('TF values:')
    print('\t coef: {}'.format(tf_model.get_from_model('params/coeff_0').ravel()))
    print('\t int: {}'.format(tf_model.get_from_model('params/intercept_0').ravel()))

    try:
        corr = np.mean(
            zscore(tf_model.predict([X])[0].ravel()) *
            zscore(sk_model.predict_proba(X)[:, 1].ravel())
        )
    except AttributeError:
        corr = np.mean(
            zscore(tf_model.predict([X])[0].ravel()) *
            zscore(sk_model.predict(X).ravel())
        )

    print('Model Correlation')
    print('\tr = {:.2f}'.format(corr))


def test_linear_regr(in_dim=2):
    """Compare tf linear regression to scikit learn
    """
    X, y = make_linear_reg_testdata(in_dim=in_dim)
    model_params = {
        'name': 'test_lin',
        'path': './tests/test_lin',
        'graph': {
            'in_sizes': [in_dim], 'out_sizes': [1], 
        }
    }

    compare_scikt_and_tf(
        sk_LinearRegression(),
        ModelWrangler(LinearRegressionModel, model_params),
        X, y)

def test_logistic_regr(in_dim=2):
    """Compare tf logistic regression to scikit learn
    """
    X, y = make_linear_cls_testdata(in_dim=in_dim)
    model_params = {
        'name': 'test_log',
        'path': './tests/test_log',
        'graph': {
            'in_sizes': [in_dim], 'out_sizes': [1], 
        }
    }

    compare_scikt_and_tf(
        sk_LogisticRegression(**{'penalty':'l2', 'C':100.0}),
        ModelWrangler(LogisticRegressionModel, model_params),
        X, y)

if __name__ == "__main__":

    model_params = {
        'name': 'test_log',
        'path': './tests/test_log',
        'graph': {
            'in_sizes': [5], 'out_sizes': [1], 
        }
    }

    print("\n\nunit testing linear regression")
    ModelTester(
        ModelWrangler(LinearRegressionModel, model_params)
    )

    print("\n\ne2e testing linear regression")
    test_linear_regr()

    print("\n\nunit testing logistic regression")
    ModelTester(
        ModelWrangler(LogisticRegressionModel, model_params)
    )

    print("\n\ne2e testing logistic regression")
    test_logistic_regr()
