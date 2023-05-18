"""motionrender package

Contents
--------

- MotionRender : class for rendering video and figures from motion capture data.
"""
from .util import load_data, load_time_series, load_joint_graph
from .plot import create_joint_frame, plot_joint_frame
from .render import update_elements, render_animation
import matplotlib.animation as animation
import matplotlib.pyplot as plt
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

        _ax_elevation default: -90 The 3d axis elevation set for rendered
            animations.
        _ax_azimuth  default: 90 The 3d axis azimuth in animations.
        _ax_roll default: None The default camera roll fo 3d rendered
            axis.

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
        self._ax_elevation = -90
        self._ax_azimuth = 90
        self._ax_roll = None
        self._ax_xlim3d = [-70, 30]
        self._ax_ylim3d = [-50, 50]
        self._ax_zlim3d = [100, 200]
        self._animation_frame_interval = 50
        #self._fig_figsize = (10, 10)
        self._animation_progress_interval = 500

        
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


    def _joint_symbol_lists(self):
        """Private utility function, given a list of joint names, return
        list of x,y,z joint names, useful in easily creating rendering
        of the joint position data.

        Parameters
        ----------
        joint_names - A simple list of string symbolic joint names being
            rendered.

        Returns
        -------
        x_joints, y_joints, z_joints - The names of all joints as we expect
        them to appear in the actual joint dataframe / sequence
        """
        x_joints = ['%sX' % name for name in self._joint_names]
        y_joints = ['%sY' % name for name in self._joint_names]
        z_joints = ['%sZ' % name for name in self._joint_names]

        return x_joints, y_joints, z_joints
 

    def _create_joint_frame(self, ax, joints):
        """Private member method _create_joint_frame
        Given a 3D ax in a figure, plot the given joint/skeleton
        points in the figure axis.

        Parameters
        ----------
        ax - a 3D matplotlib axis on which to plot the joint positions
        joints - A Pandas series or dictionary like object with joint positions
        as features or keys of the expected names.

        Returns
        -------
        fig_elements - A list of line figure elements are returned
        Implicitly  the joints are plotted on the given figure
        """
        x_joints, y_joints, z_joints = self._joint_symbol_lists()

        # pull out the x,y and z positions by joint names
        x_pos = joints[x_joints]
        y_pos = joints[y_joints]
        z_pos = joints[z_joints]

        # first scatter plot the joint positions as blue circle markers
        fig_elements = [ax.plot(x, y, z, 'bo')[0] for x,y,z in zip(x_pos, y_pos, z_pos)] 
    
        # now plot the joint skeleton graph as red lines between joint positions
        for src, dst in self._joint_graph:
            line = ax.plot([x_pos[src], x_pos[dst]],
                           [y_pos[src], y_pos[dst]],
                           [z_pos[src], z_pos[dst]],
                           'r')[0]
            fig_elements.append(line)
        
        return fig_elements
   
    def render_frame(self, time_stamp, figure_name=None, figsize=(10, 10)):
        """Render a frame of the time series.  This function expectes
        the time stamp of the frame to be rendered.  The figure is saved
        to the indicatef file name, and a matplotlib figure object is
        also created and returned from this function for dynamic
        environment visualization like Jupyter Notebooks.
        Given the joint positions at a point in time, render their
        joints and the joint graph on a 3D canvas.

        Parameters
        ----------
        time_stamp - The time stamp of the frame to be rendered into a
            figure / file.
        figure_name - The output file name to render the file into.
            Default is None, in which case no file is created for you.
            This parameter is passed to matplotlib savefig, so the
            file extension will determine the image type, e.g. png, jpg,
            svg, etc.
        figsize - default figure size is (10, 10) inches, can be overridden.

        joints - A Pandas series or dictionary like object with joint positions
            as features or keys of the expected names.
        joint_graph - The directed graph of the skeleton/connections that defines
            the joint relationships.
        joint_names - The symbolic names of the joints in the joint graph
        joints, joint_graph, joint_names, figsize=(10,10)

        Returns
        -------
        fig - This function creates and returns a matplotlib figure object
            that can be displayed or saved as a single frame image.
        """
        # we assume first feature is the time stamp, search for the joints frame
        # asked to be rendered by user
        time_stamp_name = self._time_df.columns[0]
        joints = self._time_df.loc[self._time_df[time_stamp_name] == time_stamp]
        
        # Test if didn't find the timestamp
        if joints.shape[0] != 1:
            raise Exception("Error: MotionRender.render_frame: did not find the asked for time stamp, time ranges from start=%d to end=%d in this time series" % (self._time_df.iloc[0][0], self._time_df.iloc[-1][0]))

        # need joints as a series
        joints_series = joints.iloc[0].squeeze()
        
        # create figure and 3d axis using matplotlib library
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(projection="3d")

        # render the frame
        _ = self._create_joint_frame(ax, joints_series)

        # change the axis view as asked for
        ax.view_init(elev=self._ax_elevation, azim=self._ax_azimuth, roll=self._ax_roll)

        # save the resulting figure to asked for file if asked
        if figure_name:
            try:
                fig.savefig(figure_name)
            except:
                raise Exception("Error: MotionRender.render_frame: saving frame to file, possibly bad path? <%s>" % figure_name)

        # return the fig object for interactive rendering
        return fig


    def _update_elements(self, num, time_df, ax):
        """Private member function _update_elements

        Update axis elements, method used when rendering animations.  Creates list of
        updated rendering elements for next frame and returns this list to render
        an update frame.

        Parameters
        ----------
        num - The frame number of the time series positions data being updated.
        time_df - The time series sequence to be rendered.  We don't use the object
            private _time_df because we might be rendering a subportion of a movie.
        ax - The figure axis with 3d elements being plotted into by these methods.

        Returns
        -------
        update_elements - returns the list of points / lines of elements updated by the
            animation rendering process for this next frame.
        """
        if num % self._animation_progress_interval == 0:
            print('processing frame: ', num)

        # extract joint positions to plot
        joints = time_df.iloc[num]
        
        # plot the joints
        ax.clear()
        updated_elements = self._create_joint_frame(ax, joints)
        ax.set_xlim3d([-70, 30])
        ax.set_ylim3d([-50, 50])
        ax.set_zlim3d([100, 200])

        # extract experiment response information for this time
        # the first response where response time is greater than this joint time
        # is the response block/trial we are in
        time = joints[0]
        title = 'Time: %d' % time
        ax.set_title(title)
        ax.view_init(self._ax_elevation, self._ax_azimuth)

        return updated_elements


    def render_animation(self,
                         begin_ts=None, end_ts=None,
                         movie_name=None,  figsize=(10,10)):
        """Render multiple time frames of our time series joint data into
        a movie / animation.  The function expects a start and end time stamp,
        though if not given these default to rendering all frames in the given
        time series.  The movie is saved to the indicated file name, and
        matplotlib animation library determins the video file type from the file
        extension given for the output movie name.  If the movie name is none,
        then no movie file is saved, instead the animation movie object is
        returned for dynamic interaction.  Given the joint positions in
        a time series, render each captured time step as a frame and gather
        the frames into a movie animation.

        Parameters
        ----------
        begin_ts - The starting time stamp of the frame to begin rendering with.
            If begin_ts is None then the first frame in the time series is used.
        end_ts - The ending time stamp of the frame to end the rendering with.
            If end_ts is None then the last frame in the time series is used.
        movie_name - The name of the file to save the rendered movie 
            animation into.  If None then the movie animation is not saved to 
            a file.
        figsize - Default (10,10) inches, the figure size of the canvas to
            render the animation elements onto.

        Returns
        -------
        animation - the created matplotlib animation object is returned
            from this api.  This object may be played interactivly or later
            saved.
        """
        # we assume first feature is the time stamp, search for the frame number of
        # the beginning and ending frames to be rendered for the user
        time_stamp_name = self._time_df.columns[0]
        num_frames, _ = self._time_df.shape

        if begin_ts is None:
            begin_frame = 0
        else:
            begin_frame = self._time_df.index[self._time_df[time_stamp_name] == begin_ts]
            if len(begin_frame) != 1:
                raise Exception("Error: MotionRender.render_movie: could not find begin time stamp %d" % (begin_ts))
            begin_frame = begin_frame[0]
            
        if end_ts is None:
            end_frame = num_frames
        else:
            end_frame = self._time_df.index[self._time_df[time_stamp_name] == end_ts]
            if len(end_frame) != 1:
                raise Exception("Error: MotionRender.render_movie: could not find end time stamp %d" % (end_ts))
            end_frame = end_frame[0]

        # extract the frames asked for into a new data frame
        time_df = self._time_df.iloc[begin_frame:end_frame]
        num_frames, _ = time_df.shape

        # start by plotting the first frame
        joints = time_df.iloc[0]

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(projection="3d")
        elements = self._create_joint_frame(ax, joints)

        # set view limits and positon
        # TODO: these will need to be discovered or parameterized?
        ax.set_xlim3d(self._ax_xlim3d)
        ax.set_ylim3d(self._ax_ylim3d)
        ax.set_zlim3d(self._ax_zlim3d)
        ax.view_init(self._ax_elevation, self._ax_azimuth)

        # create animation object
        ani = animation.FuncAnimation(
            fig, self._update_elements, num_frames,
            fargs=(time_df, ax), interval=self._animation_frame_interval)

        # save the resulting movie animation to asked for file if asked
        if movie_name:
            try:
                ani.save(movie_name)
            except:
                raise Exception("Error: MotionRender.render_movie: saving movie to file, possibly bad path? <%s>" % (movie_name))
        
        return ani
