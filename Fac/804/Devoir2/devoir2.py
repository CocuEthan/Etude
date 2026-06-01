# =============================================================================
# Devoir 2 – INFO0804
# Hyperparameter Tuning
# =============================================================================
import os
import warnings
import logging

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.constraints import max_norm
from scikeras.wrappers import KerasRegressor, KerasClassifier

_DIR = os.path.dirname(os.path.abspath(__file__))

EPOCHS  = 100
BATCH   = 10
CV_FOLD = 3

# ─── Utilitaire d'affichage ──────────────────────────────────────────────────
def print_grid_results(grid_result, key):
    means  = grid_result.cv_results_['mean_test_score']
    stds   = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    col_w  = max(len(str(p[key])) for p in params) + 2
    header = f"{'Valeur':<{col_w}} {'mean_test_score':>18} {'std_test_score':>16}"
    print(header)
    print("-" * len(header))
    for mean, std, param in zip(means, stds, params):
        print(f"{str(param[key]):<{col_w}} {mean:>18.6f} {std:>16.6f}")
    print(f"\n=> Optimal : {grid_result.best_params_[key]}  "
          f"(score={grid_result.best_score_:.6f})\n")


def print_dropout_results(grid_result):
    means  = grid_result.cv_results_['mean_test_score']
    stds   = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    print(f"{'Dropout':>10} {'weight_constraint':>20} {'mean_test_score':>18} {'std_test_score':>16}")
    print("-" * 68)
    for mean, std, param in zip(means, stds, params):
        dr = param['model__dropout_rate']
        wc = param['model__weight_constraint']
        print(f"{dr:>10} {wc:>20} {mean:>18.6f} {std:>16.6f}")
    bdr = grid_result.best_params_['model__dropout_rate']
    bwc = grid_result.best_params_['model__weight_constraint']
    print(f"\n=> Optimal : {{dropout={bdr}, weight_constraint={bwc}}}  "
          f"(score={grid_result.best_score_:.6f})\n")


# =============================================================================
# EXO 1 – Régression sur la base "housing" (Boston Housing)
# Architecture : 1 couche cachée de 13 neurones, sortie linéaire
# Partage : 33% test / 67% train
# =============================================================================
print("=" * 70)
print("EXO 1 – REGRESSION SUR LA BASE HOUSING")
print("=" * 70)

from keras.datasets import boston_housing
(x_tr, y_tr), (x_te, y_te) = boston_housing.load_data(seed=42)
X_housing = np.vstack([x_tr, x_te])
Y_housing  = np.concatenate([y_tr, y_te])

X_train1, X_test1, y_train1, y_test1 = train_test_split(
    X_housing, Y_housing, test_size=0.33, random_state=7
)

REG_INITS  = ['uniform', 'lecun_uniform', 'zeros',
              'glorot_normal', 'glorot_uniform', 'he_normal', 'he_uniform']
ACTIVATIONS = ['softmax', 'softplus', 'softsign', 'relu',
               'tanh', 'sigmoid', 'hard_sigmoid', 'linear']
LOSSES_REG  = ['mean_squared_error', 'mean_absolute_error',
               'mean_squared_logarithmic_error',
               'mean_absolute_percentage_error', 'cosine_similarity']
OPTIMIZERS  = ['SGD', 'RMSprop', 'Adagrad', 'Adadelta',
               'Adam', 'Adamax', 'Nadam']
DROPOUTS       = [0.0, 0.2, 0.4, 0.6, 0.9]
WEIGHT_CONSTRAINTS = [1, 2, 3]

# ─── I) Initialisation des poids ─────────────────────────────────────────────
print("\n--- I) Initialisation des poids ---")

def build_reg_init(init='glorot_uniform'):
    m = Sequential()
    m.add(Dense(13, input_dim=13, kernel_initializer=init, activation='relu'))
    m.add(Dense(1,  kernel_initializer=init))
    m.compile(loss='mean_squared_error', optimizer='adam')
    return m

reg = KerasRegressor(model=build_reg_init, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=reg,
                    param_grid=dict(model__init=REG_INITS),
                    cv=CV_FOLD, scoring='neg_mean_squared_error')
res = grid.fit(X_train1, y_train1)
print_grid_results(res, 'model__init')
best_init_reg = res.best_params_['model__init']

# ─── II) Fonction d'activation ───────────────────────────────────────────────
print("--- II) Fonction d'activation des couches cachées ---")

def build_reg_act(activation='relu'):
    m = Sequential()
    m.add(Dense(13, input_dim=13, kernel_initializer=best_init_reg, activation=activation))
    m.add(Dense(1,  kernel_initializer=best_init_reg))
    m.compile(loss='mean_squared_error', optimizer='adam')
    return m

reg = KerasRegressor(model=build_reg_act, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=reg,
                    param_grid=dict(model__activation=ACTIVATIONS),
                    cv=CV_FOLD, scoring='neg_mean_squared_error')
res = grid.fit(X_train1, y_train1)
print_grid_results(res, 'model__activation')
best_act_reg = res.best_params_['model__activation']

# ─── III) Fonction coût ──────────────────────────────────────────────────────
print("--- III) Fonction coût ---")

def build_reg_loss(loss_fn='mean_squared_error'):
    m = Sequential()
    m.add(Dense(13, input_dim=13, kernel_initializer=best_init_reg, activation=best_act_reg))
    m.add(Dense(1,  kernel_initializer=best_init_reg))
    m.compile(loss=loss_fn, optimizer='adam')
    return m

reg = KerasRegressor(model=build_reg_loss, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=reg,
                    param_grid=dict(model__loss_fn=LOSSES_REG),
                    cv=CV_FOLD, scoring='neg_mean_squared_error')
res = grid.fit(X_train1, y_train1)
print_grid_results(res, 'model__loss_fn')
best_loss_reg = res.best_params_['model__loss_fn']

# ─── IV) Optimizer ───────────────────────────────────────────────────────────
print("--- IV) L'algorithme d'optimisation ---")

def build_reg_opt(opt_name='adam'):
    m = Sequential()
    m.add(Dense(13, input_dim=13, kernel_initializer=best_init_reg, activation=best_act_reg))
    m.add(Dense(1,  kernel_initializer=best_init_reg))
    m.compile(loss=best_loss_reg, optimizer=opt_name)
    return m

reg = KerasRegressor(model=build_reg_opt, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=reg,
                    param_grid=dict(model__opt_name=OPTIMIZERS),
                    cv=CV_FOLD, scoring='neg_mean_squared_error')
res = grid.fit(X_train1, y_train1)
print_grid_results(res, 'model__opt_name')
best_opt_reg = res.best_params_['model__opt_name']

# ─── V) Dropout + weight_constraint ─────────────────────────────────────────
print("--- V) Dropout / weight_constraint ---")

def build_reg_dropout(dropout_rate=0.0, weight_constraint=1):
    m = Sequential()
    m.add(Dense(13, input_dim=13, kernel_initializer=best_init_reg,
                activation=best_act_reg, kernel_constraint=max_norm(weight_constraint)))
    m.add(Dropout(dropout_rate))
    m.add(Dense(1,  kernel_initializer=best_init_reg))
    m.compile(loss=best_loss_reg, optimizer=best_opt_reg)
    return m

reg = KerasRegressor(model=build_reg_dropout, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=reg,
                    param_grid=dict(model__dropout_rate=DROPOUTS,
                                    model__weight_constraint=WEIGHT_CONSTRAINTS),
                    cv=CV_FOLD, scoring='neg_mean_squared_error')
res = grid.fit(X_train1, y_train1)
print_dropout_results(res)
best_dropout_reg = res.best_params_['model__dropout_rate']
best_wc_reg      = res.best_params_['model__weight_constraint']

# ─── Modèle final Exo 1 ─────────────────────────────────────────────────────
print("--- Modèle final avec paramètres optimaux (Exo 1) ---")
print(f"  init        = {best_init_reg}")
print(f"  activation  = {best_act_reg}")
print(f"  loss        = {best_loss_reg}")
print(f"  optimizer   = {best_opt_reg}")
print(f"  dropout     = {best_dropout_reg},  weight_constraint = {best_wc_reg}")

final1 = Sequential()
final1.add(Dense(13, input_dim=13, kernel_initializer=best_init_reg,
                 activation=best_act_reg, kernel_constraint=max_norm(best_wc_reg)))
final1.add(Dropout(best_dropout_reg))
final1.add(Dense(1,  kernel_initializer=best_init_reg))
final1.compile(loss=best_loss_reg, optimizer=best_opt_reg, metrics=['mae'])

hist1 = final1.fit(X_train1, y_train1,
                   validation_data=(X_test1, y_test1),
                   epochs=EPOCHS, batch_size=BATCH, verbose=0)

print(f"\n{'Param':<15} {'Valeur':<20} {'Train_Loss':>12} {'Train_MAE':>12}"
      f" {'Val_Loss':>12} {'Val_MAE':>12}")
print("-" * 85)
metrics_line = lambda label, val: (
    f"{label:<15} {str(val):<20}"
    f" {hist1.history['loss'][-1]:>12.4f} {hist1.history['mae'][-1]:>12.4f}"
    f" {hist1.history['val_loss'][-1]:>12.4f} {hist1.history['val_mae'][-1]:>12.4f}"
)
print(metrics_line('Init_weight',  best_init_reg))
print(metrics_line('Fct_activation', best_act_reg))
print(metrics_line('Fct_cout',     best_loss_reg))
print(metrics_line('optimizer',    best_opt_reg))
print(metrics_line(f'Dropout/wc',  f"{best_dropout_reg}/{best_wc_reg}"))


# =============================================================================
# EXO 2 – Classification binaire sur la base "diabetes"
# Architecture : 1 couche cachée de 8 neurones, sortie sigmoid
# Partage : 33% test / 67% train
# =============================================================================
print("\n" + "=" * 70)
print("EXO 2 – CLASSIFICATION BINAIRE SUR LA BASE DIABETES")
print("=" * 70)

dataset = np.loadtxt(
    os.path.join(_DIR, '../tp2/pima-indians-diabetes.data.csv'), delimiter=','
)
X_diab = dataset[:, 0:8]
Y_diab = dataset[:, 8]

X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X_diab, Y_diab, test_size=0.33, random_state=7
)

LOSSES_CLS = ['binary_crossentropy', 'binary_focal_crossentropy', 'cosine_similarity']

# ─── I) Initialisation des poids ─────────────────────────────────────────────
print("\n--- I) Initialisation des poids ---")

def build_cls_init(init='glorot_uniform'):
    m = Sequential()
    m.add(Dense(8, input_dim=8, kernel_initializer=init, activation='relu'))
    m.add(Dense(1, kernel_initializer=init, activation='sigmoid'))
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

clf = KerasClassifier(model=build_cls_init, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=clf,
                    param_grid=dict(model__init=REG_INITS),
                    cv=CV_FOLD)
res = grid.fit(X_train2, y_train2)
print_grid_results(res, 'model__init')
best_init_cls = res.best_params_['model__init']

# ─── II) Fonction d'activation ───────────────────────────────────────────────
print("--- II) Fonction d'activation des couches cachées ---")

def build_cls_act(activation='relu'):
    m = Sequential()
    m.add(Dense(8, input_dim=8, kernel_initializer=best_init_cls, activation=activation))
    m.add(Dense(1, kernel_initializer=best_init_cls, activation='sigmoid'))
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

clf = KerasClassifier(model=build_cls_act, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=clf,
                    param_grid=dict(model__activation=ACTIVATIONS),
                    cv=CV_FOLD)
res = grid.fit(X_train2, y_train2)
print_grid_results(res, 'model__activation')
best_act_cls = res.best_params_['model__activation']

# ─── III) Fonction coût ──────────────────────────────────────────────────────
print("--- III) Fonction coût ---")

def build_cls_loss(loss_fn='binary_crossentropy'):
    m = Sequential()
    m.add(Dense(8, input_dim=8, kernel_initializer=best_init_cls, activation=best_act_cls))
    m.add(Dense(1, kernel_initializer=best_init_cls, activation='sigmoid'))
    m.compile(loss=loss_fn, optimizer='adam', metrics=['accuracy'])
    return m

clf = KerasClassifier(model=build_cls_loss, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=clf,
                    param_grid=dict(model__loss_fn=LOSSES_CLS),
                    cv=CV_FOLD)
res = grid.fit(X_train2, y_train2)
print_grid_results(res, 'model__loss_fn')
best_loss_cls = res.best_params_['model__loss_fn']

# ─── IV) Optimizer ───────────────────────────────────────────────────────────
print("--- IV) L'algorithme d'optimisation ---")

def build_cls_opt(opt_name='adam'):
    m = Sequential()
    m.add(Dense(8, input_dim=8, kernel_initializer=best_init_cls, activation=best_act_cls))
    m.add(Dense(1, kernel_initializer=best_init_cls, activation='sigmoid'))
    m.compile(loss=best_loss_cls, optimizer=opt_name, metrics=['accuracy'])
    return m

clf = KerasClassifier(model=build_cls_opt, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=clf,
                    param_grid=dict(model__opt_name=OPTIMIZERS),
                    cv=CV_FOLD)
res = grid.fit(X_train2, y_train2)
print_grid_results(res, 'model__opt_name')
best_opt_cls = res.best_params_['model__opt_name']

# ─── V) Dropout + weight_constraint ─────────────────────────────────────────
print("--- V) Dropout / weight_constraint ---")

def build_cls_dropout(dropout_rate=0.0, weight_constraint=1):
    m = Sequential()
    m.add(Dense(8, input_dim=8, kernel_initializer=best_init_cls,
                activation=best_act_cls, kernel_constraint=max_norm(weight_constraint)))
    m.add(Dropout(dropout_rate))
    m.add(Dense(1, kernel_initializer=best_init_cls, activation='sigmoid'))
    m.compile(loss=best_loss_cls, optimizer=best_opt_cls, metrics=['accuracy'])
    return m

clf = KerasClassifier(model=build_cls_dropout, epochs=EPOCHS, batch_size=BATCH, verbose=0)
grid = GridSearchCV(estimator=clf,
                    param_grid=dict(model__dropout_rate=DROPOUTS,
                                    model__weight_constraint=WEIGHT_CONSTRAINTS),
                    cv=CV_FOLD)
res = grid.fit(X_train2, y_train2)
print_dropout_results(res)
best_dropout_cls = res.best_params_['model__dropout_rate']
best_wc_cls      = res.best_params_['model__weight_constraint']

# ─── Modèle final Exo 2 ─────────────────────────────────────────────────────
print("--- Modèle final avec paramètres optimaux (Exo 2) ---")
print(f"  init        = {best_init_cls}")
print(f"  activation  = {best_act_cls}")
print(f"  loss        = {best_loss_cls}")
print(f"  optimizer   = {best_opt_cls}")
print(f"  dropout     = {best_dropout_cls},  weight_constraint = {best_wc_cls}")

final2 = Sequential()
final2.add(Dense(8, input_dim=8, kernel_initializer=best_init_cls,
                 activation=best_act_cls, kernel_constraint=max_norm(best_wc_cls)))
final2.add(Dropout(best_dropout_cls))
final2.add(Dense(1, kernel_initializer=best_init_cls, activation='sigmoid'))
final2.compile(loss=best_loss_cls, optimizer=best_opt_cls, metrics=['accuracy'])

hist2 = final2.fit(X_train2, y_train2,
                   validation_data=(X_test2, y_test2),
                   epochs=EPOCHS, batch_size=BATCH, verbose=0)

print(f"\n{'Param':<15} {'Valeur':<30} {'Train_Loss':>12} {'Train_Acc':>12}"
      f" {'Val_Loss':>12} {'Val_Acc':>12}")
print("-" * 97)
metrics_line2 = lambda label, val: (
    f"{label:<15} {str(val):<30}"
    f" {hist2.history['loss'][-1]:>12.4f} {hist2.history['accuracy'][-1]:>12.4f}"
    f" {hist2.history['val_loss'][-1]:>12.4f} {hist2.history['val_accuracy'][-1]:>12.4f}"
)
print(metrics_line2('Init_weight',  best_init_cls))
print(metrics_line2('Fct_activation', best_act_cls))
print(metrics_line2('Fct_cout',     best_loss_cls))
print(metrics_line2('optimizer',    best_opt_cls))
print(metrics_line2('Dropout/wc',   f"{best_dropout_cls}/{best_wc_cls}"))
