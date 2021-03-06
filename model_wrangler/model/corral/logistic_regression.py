"""Module sets up Logistic Regression model"""

# pylint: disable=R0914

import tensorflow as tf

from model_wrangler.architecture import BaseArchitecture
from model_wrangler.model.losses import loss_sigmoid_ce


class LogisticRegressionModel(BaseArchitecture):
    """Logistic regression"""

    def setup_layers(self, params):
        """Build all the model layers"""

        #
        # Load params
        #

        in_sizes = params.get('in_sizes', [])
        out_sizes = params.get('out_sizes', [])

        #
        # Build model
        #

        in_layers = [
            tf.placeholder("float", name="input_{}".format(idx), shape=[None, in_size])
            for idx, in_size in enumerate(in_sizes)
        ]

        with tf.variable_scope('params'):
            coeffs = [
                tf.Variable(tf.ones([size, 1]), name="coeff_{}".format(idx))
                for idx, size in enumerate(in_sizes)
            ]

            intercepts = [
                tf.Variable(tf.zeros([1, ]), name="intercept_{}".format(idx))
                for idx, _ in enumerate(in_sizes)
            ]

        out_layers_preact = [
            tf.add(tf.matmul(in_layers[0], coeff), intercept, name="output_{}".format(idx))
            for idx, (coeff, intercept) in enumerate(zip(coeffs, intercepts))
        ]

        out_layers = [
            tf.sigmoid(layer, name='output_{}'.format(idx))
            for idx, layer in enumerate(out_layers_preact)
        ]

        target_layers = [
            tf.placeholder("float", name="target_{}".format(idx), shape=[None, out_size])
            for idx, out_size in enumerate(out_sizes)
        ]

        #
        # Set up loss
        #

        loss = tf.reduce_sum(
            [loss_sigmoid_ce(*pair) for pair in zip(out_layers_preact, target_layers)]
        )

        embeds = None
        tb_scalars = {}
        return in_layers, out_layers, target_layers, embeds, loss, tb_scalars
