from motionrender.util import load_data
from motionrender.render import render_animation
import matplotlib.pyplot as plt
import os

good_time_series = "data/good_time_series.csv"
good_joint_graph = "data/good_joint_graph.csv"
good_animation = "figures/good_animation.mov"


def test_render_animation():
    time_df, joint_graph, joint_names = load_data(good_time_series, good_joint_graph)
    ani = render_animation(time_df, joint_graph, joint_names)
    if not os.path.exists('figures'):
        os.mkdir('figures')
    ani.save(good_animation)
