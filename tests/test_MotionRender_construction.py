from motionrender import MotionRender
import pytest


# globals used in testing
good_time_series = "data/good_time_series.csv"
good_joint_graph = "data/good_joint_graph.csv"
inconsistant_name_time_series = "data/inconsistent_name_time_series.csv"
malformed_joint_graph = "data/malformed_joint_graph.csv"
name_mismatch_time_series = "data/name_mismatch_time_series.csv"
num_mismatch_time_series = "data/num_mismatch_time_series.csv"


# TODO: should probably create specific exceptions and expect them here
def test_good_time_series():
    mr = MotionRender(good_time_series, good_joint_graph)
    time_df, joint_names = mr._load_time_series(good_time_series)
    assert time_df.shape == (4, 13)
    assert joint_names == ['head', 'neck', 'leftShoulder', 'rightShoulder']

def test_inconsistant_names():
    with pytest.raises(Exception, match=r".* joint symbolic names are malformed: .*"):
        mr = MotionRender(inconsistant_name_time_series, good_joint_graph)
    
def test_good_joint_graph():
    mr = MotionRender(good_time_series, good_joint_graph)
    joint_graph, joint_names = mr._load_joint_graph(good_joint_graph)
    assert len(joint_graph) == 3
    assert joint_graph[2] == (1, 3)
    assert joint_names == ['head', 'neck', 'leftShoulder', 'rightShoulder']

def test_malformed_graph():
    with pytest.raises(Exception, match=r".* malformed graph edge line .*"):
        mr = MotionRender(good_time_series, malformed_joint_graph)
    
def test_good_construct():
    mr = MotionRender(good_time_series, good_joint_graph)
    assert mr._time_df.shape == (4, 13)
    assert len(mr._joint_graph) == 3
    assert mr._joint_graph[2] == (1, 3)
    assert mr._joint_names == ['head', 'neck', 'leftShoulder', 'rightShoulder']

def test_mismatch_columns():
    with pytest.raises(Exception, match=r".* got unexpected number of columns .*"):
        mr = MotionRender(num_mismatch_time_series, good_joint_graph)
    
def test_mismatch_names():
    with pytest.raises(Exception, match=r".* names specified for joints do not match.*"):
        mr = MotionRender(name_mismatch_time_series, good_joint_graph)
    
def test_bad_time_series_file():
    with pytest.raises(Exception, match=r".* file not found .*"):
        mr = MotionRender("bogus_time_series_file.csv", good_joint_graph)

def test_bad_joint_graph_file():
    with pytest.raises(Exception, match=r".* file not found .*"):
        mr = MotionRender(good_time_series, "bogus_joint_graph_file.csv")
 
