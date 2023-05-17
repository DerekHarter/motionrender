from motionrender.util import load_data, load_time_series, load_joint_graph
import pandas as pd

# globals used in testing
good_time_series = "data/good_time_series.csv"
good_joint_graph = "data/good_joint_graph.csv"

def test_good_time_series():
    time_df, N, joint_names = load_time_series(good_time_series)
    assert time_df.shape == (4, 13)
    assert N == 4
    assert joint_names == ['head', 'neck', 'leftShoulder', 'rightShoulder']

def test_good_joint_graph():
    joint_graph, N, joint_names = load_joint_graph(good_joint_graph)
    assert len(joint_graph) == 3
    assert joint_graph[2] == (1, 3)
    assert N == 4
    assert joint_names == ['head', 'neck', 'leftShoulder', 'rightShoulder']

def test_good_load():
    time_df, joint_graph, N, joint_names = load_data(good_time_series, good_joint_graph)
    assert time_df.shape == (4, 13)
    assert len(joint_graph) == 3
    assert joint_graph[2] == (1, 3)
    assert N == 4
    assert joint_names == ['head', 'neck', 'leftShoulder', 'rightShoulder']
    
