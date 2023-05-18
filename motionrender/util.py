"""Utility functions

Utility function for the load data module
"""
import pandas as pd
import re

def load_data(time_series_file, joint_graph_file):
    """Load time series and joint graph data files.

    We expect both files to be properly formated for their
    respective load/parse functions.

    We expect the files to have related information in this file, which
    should match across the two files.

    Parameters
    ----------
    time_series_file - The name of the file of joint position time series data to load and
       parse.
    joint_graph_file - The name of the file that holds the joint graph data.

    Returns
    -------
    time_df - For the moment we use pandas and return a pandas data frame of the loaded
        time series.
    joint_graph - A data structure used in rendering that defines the connected joint
        graph.
    joint_names - A list of the names, in the example these are 
        [head, neck, leftShoulder, rightShoulder]

    """
    time_df, joint_names_time = load_time_series(time_series_file)
    joint_graph, joint_names_graph = load_joint_graph(joint_graph_file)

    if len(joint_names_time) != len(joint_names_graph):
        raise Exception("ERROR: motionrender: load_time_data: mismatching time series and joint graph data, number of joints are mismatched")

    if joint_names_time != joint_names_graph:
        raise Exception("ERROR: motionrender: load_time_data: mismatching time series and joint graph data, names specified for joints do not match")

    return time_df, joint_graph, joint_names_time


def load_time_series(time_series_file):
    """Load a time series data file.  We expect the time series file to be
    a regular comma separated values file.  It should have a header line with
    symbolic names for the joints, and be of this format

    timeStamp, headX, headY, headZ, neckX, neckY, neckZ, leftShoulderX, leftShouldY, leftShoulderZ, rightShoulderX, rightShoulderY, rightShoulderZ
    1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4
    ...  time 2 thorugh N positions

    We expect the first feature to be a time stampe (can be for example utc in milliseconds).
    There should be 3 * N columns, where N are the number of joints that were captured and
    tracked by the motion tracking system that generates the data.  Each tracked point should
    have 3 values, and X,Y,Z position of the joint at the given time stamp.

    Parameters
    ----------
    time_series_file - The name of the file of joint position time series data to load and
       parse.

    Returns
    -------
    time_df - For the moment we use pandas and return a pandas data frame of the loaded
        time series.
    joint_names - A list of the names, in the example these are 
        [head, neck, leftShoulder, rightShoulder]
    """
    # do initial load of the data
    time_df = pd.read_csv(time_series_file)
    time_df.columns = time_df.columns.str.strip()
    
    # determine N the number of joints and check that data has expected format
    N_3d = len(time_df.columns) - 1
    if N_3d % 3 != 0:
        raise Exception("ERROR: motionrender: load_time_series: expected 3D points in columns, but got unexpected number of columns of data")
    N = N_3d // 3

    # determine the joint names list, check that all joint names have expected names
    joint_names = []
    for n in range(N):
        # extract the X,Y,Z joint names for each joint n,
        # chop off last character expected to indicate X,Y,Z position of joint
        joint_x = time_df.columns[n * 3 + 1][:-1].strip()
        joint_y = time_df.columns[n * 3 + 2][:-1].strip()
        joint_z = time_df.columns[n * 3 + 3][:-1].strip()

        if joint_x != joint_y or joint_y != joint_z:
            raise Exception("ERROR: motionrender: load_time_series: joint symbolic names are malformed: (%s, %s, %s", (joint_x, joint_y, joint_z))
        
        # append joint name to end of list
        joint_names.append(joint_x)
    
    return time_df, joint_names


def load_joint_graph(joint_graph_file):
    """Load a joint graph data file.  We expect each joint graph file to be defined
    in the following format:

    head neck
    neck leftShoulder
    neck rightShoulder

    Each line represents a connection between given joints in the graph.
    The connection graph is what is rendered at each time series point,
    the sequence of which forms an animation/visualization of the joint 
    positions moving over time.

    Parameters
    ----------
    joint_graph_file - The name of the file that holds the joint graph data.

    Returns
    -------
    joint_graph - A data structure used in rendering that defines the connected joint
        graph.
    joint_names - The list of joint names in the graph
    """
    joint_dict = {}
    joint_graph = []
    joint_names = []
    N = 0

    # each line has a pait of joints describing an edge in the joint graph
    # between nodes.  Parse each line and build the joint graph and list
    # of names
    pattern = r"^(\w+)\s+(\w+)$"
    for line in open(joint_graph_file).readlines():
        match = re.search(pattern, line)

        # parse the graph edge on this line
        if not match:
            raise Exception("Error: motionrender: load_joint_graph: malformed graph edge line in the joint graph <%s>" % line)

        joint1 = match.group(1)
        joint2 = match.group(2)
        
        # determine the joint identifier and insert into joint names if a new name
        if not joint1 in joint_dict:
            joint_dict[joint1] = N
            N = N + 1
            joint_names.append(joint1)
        joint1_id = joint_dict[joint1]
        
        if not joint2 in joint_dict:
            joint_dict[joint2] = N
            N = N + 1
            joint_names.append(joint2)
        joint2_id = joint_dict[joint2]
        
        # insert the edge into the joint graph structure
        joint_graph.append( (joint1_id, joint2_id) )

    return joint_graph, joint_names
