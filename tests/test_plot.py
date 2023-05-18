from motionrender.util import load_data
from motionrender.plot import joint_symbol_lists, create_joint_frame, plot_joint_frame
import matplotlib.pyplot as plt
import os

good_time_series = "data/good_time_series.csv"
good_joint_graph = "data/good_joint_graph.csv"
good_figure = "figures/good_figure.png"


def test_joint_symbol_lists():
    time_df, joint_graph, joint_names = load_data(good_time_series, good_joint_graph)
    x_joints, y_joints, z_joints = joint_symbol_lists(joint_names)
    num_joints = len(joint_names)
    assert len(x_joints) == num_joints
    assert len(y_joints) == num_joints
    assert len(z_joints) == num_joints
    assert x_joints[0] == 'headX'
    assert y_joints[0] == 'headY'
    assert z_joints[0] == 'headZ'
    
def test_create_joint_frame():
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(projection="3d")

    time_df, joint_graph, joint_names = load_data(good_time_series, good_joint_graph)
    joints = time_df.iloc[1]
    lines = create_joint_frame(ax, joints, joint_graph, joint_names)
    assert len(lines) == 7 # 4 points and 3 lines as elements

def test_plot_joint_frame():
    time_df, joint_graph, joint_names = load_data(good_time_series, good_joint_graph)
    joint_frame = time_df.iloc[1]
    fig = plot_joint_frame(joint_frame, joint_graph, joint_names)
    if not os.path.exists('figures'):
        os.mkdir('figures')
    fig.savefig(good_figure)
