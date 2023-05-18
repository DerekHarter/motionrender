from motionrender import MotionRender
import matplotlib.pyplot as plt
import os
import pytest

# globals used in testing
good_time_series = "data/good_time_series.csv"
good_joint_graph = "data/good_joint_graph.csv"
good_figure = "figures/good_figure.png"

def test_joint_symbol_lists():
    mr = MotionRender(good_time_series, good_joint_graph)
    
    x_joints, y_joints, z_joints = mr._joint_symbol_lists()
    num_joints = len(mr._joint_names)
    
    assert len(x_joints) == num_joints
    assert len(y_joints) == num_joints
    assert len(z_joints) == num_joints
    assert x_joints[0] == 'headX'
    assert y_joints[0] == 'headY'
    assert z_joints[0] == 'headZ'
    
def test_create_joint_frame():
    mr = MotionRender(good_time_series, good_joint_graph)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection="3d")
    joints = mr._time_df.iloc[1]
    lines = mr._create_joint_frame(ax, joints)

    assert len(lines) == 7 # 4 points and 3 lines as elements


def test_render_frame():
    mr = MotionRender(good_time_series, good_joint_graph)

    if not os.path.exists('figures'):
        os.mkdir('figures')

    mr.render_frame(1, good_figure)

def test_bad_time_stamp():
    mr = MotionRender(good_time_series, good_joint_graph)

    if not os.path.exists('figures'):
        os.mkdir('figures')

    with pytest.raises(Exception, match=r".* did not find the asked for time stamp, .*"):
        mr.render_frame(5, good_figure)
    

def test_bad_filename():
    mr = MotionRender(good_time_series, good_joint_graph)

    with pytest.raises(Exception, match=r".* saving frame to file, .*"):
        mr.render_frame(2, "bad_figures/bogus_output_file.png")

def test_figure_object_return():
    mr = MotionRender(good_time_series, good_joint_graph)

    mr._ax_elevation = -10
    mr._ax_azimuth = 240
    fig = mr.render_frame(3, figsize=(12, 8))
    assert fig.get_dpi() == 100
    assert fig.get_figwidth() == 12.0
    assert fig.get_figheight() == 8.0
    assert fig.axes[0].elev == -10
    assert fig.axes[0].azim == 240
