"""Module sets up Dense Autoencoder model"""

# pylint: disable=R0914 
import numpy as np
import tensorflow as tf

from tensorflow import keras
from keras.layers import Dense, TimeDistributed

from model_wrangler.architecture import BaseArchitecture
from model_wrangler.model.layers import append_dense
from model_wrangler.model.losses import loss_mse

class LstmModel(BaseArchitecture):
    """Dense Feedforward"""

    # pylint: disable=too-many-instance-attributes

    def setup_training_step(self, params):
        """Set up loss and training step"""

        # Import params
        learning_rate = params.get('learning_rate', 0.01)

        optimizer = tf.train.RMSPropOptimizer(learning_rate)

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            train_step = optimizer.minimize(self.loss)

        return train_step

    def setup_layers(self, params):
        """Build all the model layers"""

        #
        # Load params
        #

        in_sizes = params.get('in_sizes', [])
        dense_params = params.get('dense_params', [])
        recurr_params = params.get('recurr_params', [])
        out_sizes = params.get('out_sizes', [])

        #
        # Build model
        #

        in_layers = [
            tf.placeholder("float", name="input_{}".format(idx), shape=[None] + in_size)
            for idx, in_size in enumerate(in_sizes)
        ]

        # Add layers on top of each input
        layer_stacks = {}
        for idx_source, in_layer in enumerate(in_layers):

            with tf.variable_scope('source_{}'.format(idx_source)):
                layer_stacks[idx_source] = [in_layer]

                for idx, layer_param in enumerate(dense_params):
                    with tf.variable_scope('conv_{}'.format(idx)):
                        layer_stacks[idx_source].append(
                            TimeDistributed(
                                Dense(
                                    layer_param.get('num_units', 3),
                                    activation=layer_param.get('activation', None),
                                    use_bias=layer_param.get('bias', True)
                                ),
                                input_shape=layer_stacks[idx_source][-1].get_shape().as_list()[2:],
                                name='dense_{}'.format(idx)
                            )(layer_stacks[idx_source][-1])
                        )

                for idx, layer_param in enumerate(recurr_params):

                    last_layer = idx == (len(recurr_params) - 1)
                    with tf.variable_scope('lstms_{}'.format(idx)):
                        layer_stacks[idx_source].append(
                            tf.keras.layers.LSTM(
                                stateful=False,
                                return_sequences=not last_layer,
                                **layer_param
                            )(layer_stacks[idx_source][-1])
                        )


        embeds = tf.concat([
            tf.contrib.layers.flatten(layer_stack[-1])
            for layer_stack in layer_stacks.values()
        ], axis=-1)


        out_layer_preact = [
            tf.expand_dims(
                append_dense(self, embeds, {'num_units': out_size}, 'preact_{}'.format(idx)),
            1)
            for idx, out_size in enumerate(out_sizes)
        ]

        out_layers = out_layer_preact

        target_layers = [
            tf.expand_dims(
                tf.placeholder("float", name="target_{}".format(idx), shape=[None, out_size]),
            1)
            for idx, out_size in enumerate(out_sizes)
        ]

        #
        # Set up loss
        #

        loss = tf.reduce_sum(
            [loss_mse(*pair) for pair in zip(out_layer_preact, target_layers)]
        )

        return in_layers, out_layers, target_layers, embeds, loss
