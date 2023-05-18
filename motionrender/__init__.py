"""motionrender package

Contents
--------

- MotionRender : class for rendering video and figures from motion capture data.
"""
from .util import load_data, load_time_series, load_joint_graph
from .plot import create_joint_frame, plot_joint_frame
from .render import update_elements, render_animation
import os
import pandas as pd
import re

class MotionRender:
    """The MotionRender class loads 3D motion capture time series data
    and provides methods to render frames of the capture joints as
    figures or sequences of the captured time series as video files.
    """
    def __init__(self, time_series_file, joint_graph_file):
        """MotionRender constructor

        The constructor takes a time series of 3D motion capture points and
        a file defining the joint graph relationships.

        Parameters
        ----------
        time_series_file - The time series file has the following simple format:

            timeStamp, headX, headY, headZ, neckX, neckY, neckZ, leftShoulderX, leftShoulderY, leftShoulderZ, rightShoulderX, rightShoulderY, rightShoulderZ
            timeStamp1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4
            timeStamp2, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8

            The first column represents a time stamp for the capture
            positions of the joints being tracked.  Then this class
            expectes a simple sequence of 3D position measurements for
            each joint tracked.  The name of the joint, for example
            headX, headY, headZ indicates a joint postion tracked
            called head.

        joint_graph_file - The joint graph defines the relationships
            of the tracked joints for plotting.  The joint names must
            correspond to the time series column feature names.  For
            example, the joint graph of the above data might have the
            following graph edges defined:

            head neck
            neck leftShoulder 
            neck rightShoulder   

        Attributes
        ----------
        The following attributes of this class currently can be set
        programatically after creating the MotionCapture instance to
        affect rendering and other properties:

        """
        # save private variables
        self._time_series_file = time_series_file
        self._joint_graph_file = joint_graph_file

        # infer time_df, joint_graph and joint_names from the time series
        # and joint graph files given, these methods provide some
        # error checking of the file formats
        self._time_df, self._joint_names = self._load_time_series(self._time_series_file)
        self._joint_graph, joint_names_graph = self._load_joint_graph(self._joint_graph_file)

        # further error check the input file information
        if len(self._joint_names) != len(joint_names_graph):
            raise Exception("ERROR: MotionRender.__init__: mismatching time series and joint graph data, number of joints are mismatched")
        if self._joint_names != joint_names_graph:
            raise Exception("ERROR: MotionRender.__init__: mismatching time series and joint graph data, names specified for joints do not match")

        # ensure column names do not contain spaces from parse
        self._time_df.columns = self._time_df.columns.str.strip()
        
        # set class attribute defaults


    def _load_time_series(self, time_series_file):
        """Private class method _load_time_series
        Load a time series data file.  We expect the time series file to be
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
        # fail gracefully if bad file name given
        if not os.path.exists(time_series_file):
            raise Exception("Error: MotionRender._load_time_series: file not found <%s>" % time_series_file)
        
        # do initial load of the data
        time_df = pd.read_csv(time_series_file)
        time_df.columns = time_df.columns.str.strip()
    
        # determine N the number of joints and check that data has expected format
        N_3d = len(time_df.columns) - 1
        if N_3d % 3 != 0:
            raise Exception("ERROR: MotionRender._load_time_series: expected 3D points in columns, but got unexpected number of columns of data")
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
                raise Exception("ERROR: MotionRender._load_time_series: joint symbolic names are malformed: (%s, %s, %s)", (joint_x, joint_y, joint_z))
        
            # append joint name to end of list
            joint_names.append(joint_x)
    
        return time_df, joint_names


    def _load_joint_graph(self, joint_graph_file):
        """Private class method _load_joint_graph
        Load a joint graph data file.  We expect each joint graph file to be defined
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
        # fail gracefully if file does not exists
        if not os.path.exists(joint_graph_file):
            raise Exception("Error: MotionRender._load_joint_graph: file not found <%s>" % joint_graph_file)
        
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
                raise Exception("Error: MotionRender._load_joint_graph: malformed graph edge line in the joint graph <%s>" % line)

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
