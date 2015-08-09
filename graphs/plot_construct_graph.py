import matplotlib.pyplot as plt
import numpy as np
import pickle
from meeg_preprocessing.utils import setup_provenance
from scripts.config import paths
from gat.gif import Figtodat
from gat.gif.images2gif import writeGif
from gat.graphs import plot_graph


report, run_id, _, logger = setup_provenance(
    script=__file__, results_dir=paths('report'))

# load data
stats_fname = paths('score', subject='fsaverage', data_type='erf',
                    analysis=('stats_target_circAngle'))
with open(stats_fname, 'rb') as f:
    out = pickle.load(f)
    scores = out['scores']
    p_values = out['p_values']
    times = out['times']

# trim significance
connectivity = np.mean(scores, axis=0)
connectivity *= p_values < .05

# animation construction
images = list()
for iteration in np.logspace(0, 2.1, 25):
    print iteration
    fig, ax = plt.subplots(1, figsize=[10, 10], facecolor='w')
    G, nodes, = plot_graph(connectivity,
                           negative_weights=True, edge_alpha=.2, node_alpha=1.,
                           weights_scale=iteration, ax=ax,
                           iterations=int(iteration) - 1,
                           node_size=100, edge_color=plt.get_cmap('RdBu_r'),
                           clim=[-.10, .10], final_pos='horizontal')
    nodes._alpha = 0.
    nodes.set_edgecolors((1., 1., 1., 0.))
    im = Figtodat.fig2img(fig)
    images.append(im)
writeGif("network_construction.gif", images)
report.add_images_to_section("network_construction.gif", 'animation', 'build')

# snapshots construction
fig, axes = plt.subplots(1, 3, figsize=[11, 4], facecolor='w')
for iteration, ax in zip(np.logspace(0, 1.5, 3), axes):
    G, nodes, = plot_graph(connectivity,
                           negative_weights=True, edge_alpha=.2, node_alpha=1.,
                           weights_scale=iteration, ax=ax,
                           iterations=int(iteration) - 1,
                           node_size=50, edge_color=plt.get_cmap('RdBu_r'),
                           clim=[-.10, .10], final_pos='horizontal')
    nodes._alpha = 0.
    nodes.set_edgecolors((1., 1., 1., 0.))
    ax.patch.set_visible(False)
report.add_figs_to_section(fig, 'snapshot', 'build')

# final construction
fig, ax = plt.subplots(1, figsize=[10, 10], facecolor='w')
node_size = np.abs(np.diagonal(connectivity) * 1000)
G, nodes, = plot_graph(connectivity,
                       negative_weights=True, edge_alpha=.2, node_alpha=.5,
                       weights_scale=50, ax=ax, iterations=100,
                       node_size=node_size, edge_color=plt.get_cmap('RdBu_r'),
                       clim=[-.10, .10], final_pos='horizontal')
nodes._alpha = 0.
nodes.set_edgecolors((1., 1., 1., 0.))
ax.patch.set_visible(False)
report.add_figs_to_section(fig, 'final', 'build')
report.save()