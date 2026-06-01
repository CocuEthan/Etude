import os
import warnings
import logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

_DIR = os.path.dirname(os.path.abspath(__file__))
import numpy
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.callbacks import LearningRateScheduler
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

seeds_data = numpy.loadtxt(os.path.join(_DIR, '..', 'tp3', 'seeds', 'seeds_dataset.txt'))
X_data = seeds_data[:, 0:7]
Y_data = to_categorical(seeds_data[:, 7] - 1, num_classes=3)
x_train, x_test, y_train, y_test = train_test_split(X_data, Y_data, test_size=0.33, random_state=7)
batch_size = 10
epochs = 150

def build_model():
    m = Sequential([
        Input(shape=(7,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(3, activation='softmax')
    ])
    return m

def decayed_learning_rate(step):
    return initial_learning_rate / (1 + decay_rate * step / decay_step)

from keras.optimizers.schedules import InverseTimeDecay
# Inverse Time Decay
lr_schedule = InverseTimeDecay(0.003, 100, 0.5)
grad_descent = SGD(learning_rate=lr_schedule)
model = build_model()
# compile the model
model.compile(optimizer=grad_descent, loss="categorical_crossentropy",
metrics=["accuracy"])
# train  the model
model.fit(x_train, y_train, validation_data=([x_test, y_test]),
batch_size=batch_size, epochs=epochs, verbose=1)

def decayed_learning_rate(step):
    step = min(step, decay_steps)
    return ((initial_learning_rate - end_learning_rate) * (1 - step / decay_steps) ^ (power) ) + end_learning_rate

from keras.optimizers.schedules import ExponentialDecay

init_lr = 0.001
lr_schedule = ExponentialDecay(init_lr, decay_steps=500, decay_rate=0.98, staircase=True)
optimizer = SGD(learning_rate=lr_schedule)
model = build_model()
# compile the model
model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])
# train the model
model.fit(x_train, y_train, validation_data=([x_test, y_test]), batch_size=batch_size, epochs=epochs, verbose=1)

def custom_lr_scheduler(epoch, current_lr):
    return current_lr / 3

lr_schedule = LearningRateScheduler(custom_lr_scheduler)
grad_descent = SGD(learning_rate=0.001)
model = build_model()
# compile the model
model.compile(optimizer=grad_descent, loss="categorical_crossentropy", metrics=["accuracy"])
# train the model
model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs,
validation_data=(x_test,y_test), callbacks=[lr_schedule], verbose=1)
