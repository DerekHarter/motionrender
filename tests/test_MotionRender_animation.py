from motionrender import MotionRender
import matplotlib.pyplot as plt
import os
import pytest


good_time_series = "data/good_time_series.csv"
good_joint_graph = "data/good_joint_graph.csv"
good_animation = "figures/good_animation.mov"
good_animation_slice = "figures/good_animation_slice.mov"


def test_render_animation():
    mr = MotionRender(good_time_series, good_joint_graph)

    if not os.path.exists('figures'):
        os.mkdir('figures')
    ani = mr.render_animation(movie_name=good_animation)

def test_render_someframes():
    mr = MotionRender(good_time_series, good_joint_graph)

    if not os.path.exists('figures'):
        os.mkdir('figures')
    ani = mr.render_animation(begin_ts=2, end_ts=3, movie_name=good_animation_slice)
    

def test_bad_begin_time_stamp():
    mr = MotionRender(good_time_series, good_joint_graph)

    if not os.path.exists('figures'):
        os.mkdir('figures')

    # good data only has time stamps from 1 to 4
    with pytest.raises(Exception, match=r".* could not find begin time stamp .*"):
        ani = mr.render_animation(begin_ts=0, end_ts=3)
    
def test_bad_end_time_stamp():
    mr = MotionRender(good_time_series, good_joint_graph)

    if not os.path.exists('figures'):
        os.mkdir('figures')

    # good data only has time stamps from 1 to 4
    with pytest.raises(Exception, match=r".* could not find end time stamp .*"):
        ani = mr.render_animation(begin_ts=2, end_ts=5)
    
