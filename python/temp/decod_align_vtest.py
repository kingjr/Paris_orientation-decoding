import pickle
import os.path as op
import numpy as np
import matplotlib.pyplot as plt
from pycircstat import vtest, rayleigh
from config import (subjects, data_path)
from myfunctions import realign_angle

# This is the stats across trials, but really we only need to apply a similar
# thing across subjects.
p_val = list()
angle_error_across = np.zeros([29, 29, 400, 20])
for subject in subjects:
    print(subject)
    path_gat = op.join(data_path, subject, 'mvpas',
        '{}-decod_{}_{}.pickle'.format(subject, 'orientation_target', 'SVC'))

    ###### PREPROC
    # Compute angle errors by realigning the predicted categories according to
    # true category
    # read GAT data
    with open(path_gat) as f:
        gat, contrast = pickle.load(f)

    n_time, n_test_time, n_trials, n_categories = dims = np.shape(gat.y_pred_)
    # realign to 4th angle category
    probas = realign_angle(gat, dims)

    # transform 6 categories into single angle: there are two options here,
    # try it on the pilot subject, and use weighted mean if the two are
    # equivalent
    prob2angle = 'most_likely_angle'
    if prob2angle == 'most_likely_angle':
        angle_errors = np.argmax(probas, axis=3) * np.pi / 3 + np.pi / 6
    elif prob2angle == 'weighted_mean':
        operator = np.tile(np.arange(n_categories),
                         (1, n_time, n_trials)).transpose((1, 2, 0))
        weighted_errors = np.prod(probas, operator)* np.pi / 3 - np.pi / 6
        angle_errors = np.mean(weighted_errors, axis=1)

    ####### STATS WITHIN SUBJECTS
    # Apply v test and retrieve statistics that is independent of the number of
    # trials.
    p_val_v, _ = vtest(angle_errors, 0, axis=2) # trials x time

    # apply Rayleigh test (better for of diagonal with distribution shifts, e.g.
    # on the n200, the prediction may reverse)
    p_val_ray, _ = rayleigh(angle_errors, axis=2) # trials x time

    # append scores
    p_val.append([p_val_v, p_val_ray])

    ####### STATS ACROSS SUBJECTS
    # apply Rayleigh test (better for of diagonal with distribution shifts, e.g.
    # on the n200, the prediction may reverse)
    angle_error_across[:, :, :, s] = angle_errors


mean_p_vals = np.zeros((n_time, n_test_time, len(subjects)))
for s, subject in enumerate(subjects):
    mean_p_vals[:, :, s] = -np.log10(np.array(p_val[s][1]))
plt.matshow(np.mean(mean_p_vals, axis=2), origin='lower')

## STATS ACROSS SUBJECTS
p, z = rayleigh(angle_error_across, axis=2, d=20)
plt.matshow(np.mean(z, axis=2), origin='lower')
