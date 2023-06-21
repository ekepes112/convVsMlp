from tensorflow import optimizers as opt
from keras.models import Model
from keras.layers import Input, Conv1D, MaxPool1D

from cnn_modules import residual_block_bottleneck
from ann_modules import prediction_head


def compile_model(
    l1_dense: float = 0.,
    l2_dense: float = 0.,
    input_shape: tuple = (None,),
    optimizer: opt.Optimizer = None,
    loss_func: str = None,
    eval_metrics: list = [],
    model_id: str = 'prototype',
    prediction_sizes: list = [2048, 1024],
):
    model_id = f'resnet_bottleneck_{model_id}'
    if optimizer is None:
        optimizer = opt.Adam(learning_rate=3e-4)
    if loss_func is None:
        raise ValueError('No loss function specified')

    # K.expand_dims(x, axis=1)

    model_input = Input(shape=input_shape)

    x = Conv1D(
        filters=32,  # lowered by a factor of 2 compared to the original work since we have 3 times fewer channels
        kernel_size=7,
        strides=2,
        padding='same',
        activation='relu',
    )(model_input)
    x = MaxPool1D(
        pool_size=2,
    )(x)

    for _ in range(3):
        for _ in range(3):
            x = residual_block_bottleneck(
                input_layer=x,
                filters=64,  # see motivation above, the scaling is not exact
                kernel_size=3,
            )
        x = MaxPool1D(
            pool_size=2,
        )(x)

    output = prediction_head(
        x,
        layer_sizes=prediction_sizes,
        lambda_l1=l1_dense,
        lambda_l2=l2_dense,
    )

    model = Model(
        model_input,
        output,
        name=model_id
    )

    model.compile(
        optimizer=optimizer,
        loss=loss_func,
        metrics=eval_metrics
    )

    return model
