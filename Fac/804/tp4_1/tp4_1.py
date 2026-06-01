import os
import warnings
import logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

_DIR = os.path.dirname(os.path.abspath(__file__))
import numpy
from tensorflow.keras.models import Sequential, load_model, model_from_json
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.callbacks import ModelCheckpoint

#charger la dataset diabetes
dataset = numpy.loadtxt(os.path.join(_DIR, '..', 'tp3', 'pima-indians-diabetes.data.csv'), delimiter=',')
# recuperer les données dans X et les labels dans Y
X = dataset[:, 0:8]
Y = dataset[:, 8]
# definir le modele
model = Sequential([
    Input(shape=(8,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])
# compiler le modele
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
# entrainer le modele
model.fit(X, Y, epochs=150, batch_size=10, verbose=0)
# evaluer le modele
score = model.evaluate(X, Y, verbose=0)
print("%s: %.2f%%" % (model.metrics_names[1], score[1]*100))
# sauvegarder le model + son archi ds le même fichier
model.save("model.h5")
model.save("poids_architecture_modele.h5")
print("Saved model to disk")


from keras.models import load_model
#  charger le modele
model = load_model('model.h5')
# afficher l'archi du modele
model.summary()
# charger le dataset
dataset = numpy.loadtxt(os.path.join(_DIR, '..', 'tp3', 'pima-indians-diabetes.data.csv'), delimiter=',')
# recuperer les données dans X et les labels dans Y
X = dataset[:, 0:8]
Y = dataset[:, 8]
# evaluer le modele
# pas besoin de compiler avant d'evaluer
score = model.evaluate(X, Y, verbose=0)
# afficher l'accuracy
print("%s: %.2f%%" % (model.metrics_names[1], score[1]*100))

# charger la dataset diabetes
dataset = numpy.loadtxt(os.path.join(_DIR, '..', 'tp3', 'pima-indians-diabetes.data.csv'), delimiter=',')
# recuperer les données dans X et les labels dans Y
X = dataset[:, 0:8]
Y = dataset[:, 8]
# definir le modele
model = Sequential([
    Input(shape=(8,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])
# compiler le modele
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
# entrainer le modele
model.fit(X, Y, epochs=150, batch_size=10, verbose=0)
# evaluer le modele
score = model.evaluate(X, Y, verbose=0)
print("%s: %.2f%%" % (model.metrics_names[1], score[1]*100))
# sérialiser le model vers un fichier JSON
model_json = model.to_json()
with open("architecture_modele.json", "w") as json_file:
    json_file.write(model_json)
# sérialiser les poids vers un ficheir HDF5
model.save_weights("poids_modele.h5")
print("Saved model to disk")

from keras.models import model_from_json
import os

# charger l'archi à partir du fichier JSON et créer le modele
json_file = open('architecture_modele.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# charger les poids
loaded_model.load_weights("poids_modele.h5")
print("Loaded model from disk")

# il est NECESSAIRE de compiler avant d'evaluer le modele
loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
# evaluer le modele
score = loaded_model.evaluate(X, Y, verbose=0)
# afficher laccuracy du modele
print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))


from keras.callbacks import ModelCheckpoint
# charger la base de donnees diabetes
dataset = numpy.loadtxt(os.path.join(_DIR, '..', 'tp3', 'pima-indians-diabetes.data.csv'), delimiter=',')
X = dataset[:, 0:8]
Y = dataset[:, 8]
# definir le modele
model = Sequential([
    Input(shape=(8,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])
# compiler le modele
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
# checkpoint
filepath="weights-improvement-{epoch:02d}-{val_loss:.2f}.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
callbacks_list = [checkpoint]
# entrainer le modele
model.fit(X, Y, validation_split=0.33, epochs=150, batch_size=10,
callbacks=callbacks_list, verbose=0)

from keras.callbacks import ModelCheckpoint
# charger la base de donnees diabetes
dataset = numpy.loadtxt(os.path.join(_DIR, '..', 'tp3', 'pima-indians-diabetes.data.csv'), delimiter=',')
X = dataset[:, 0:8]
Y = dataset[:, 8]
# definir le modele
model = Sequential([
    Input(shape=(8,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])
# compiler le modele
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
# checkpoint
filepath="weights-best.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1,
save_best_only=True, mode='min')
callbacks_list = [checkpoint]
# entrainer le modele
model.fit(X, Y, validation_split=0.33, epochs=150, batch_size=10,
callbacks=callbacks_list, verbose=0)
