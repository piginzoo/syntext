import tensorflow as tf


class ConvBlock(tf.keras.Model):

    def __init__(self, num_filters, kernel_size,
                 weight_decay=1e-4, dropout_rate=0.):
        super(ConvBlock, self).__init__()

        self.conv = tf.keras.layers.Conv2D(num_filters, kernel_size,
            padding="same",use_bias=False, kernel_initializer="he_normal",
            kernel_regularizer=tf.keras.regularizers.l2(weight_decay))
        self.bn = tf.keras.layers.BatchNormalization()
        self.dropout = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, training=True):
        output = self.conv(x)
        output = self.bn(x, training=training)
        output = tf.nn.relu(output)
        output = self.dropout(output, training=training)
        return output


model = ConvBlock(32, 3, 1e-4, 0.5)
x = tf.ones((4, 224, 224, 3))
y = model(x)
print(model.layers)
