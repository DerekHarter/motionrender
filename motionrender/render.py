"""Render functions

Functions to render 3d movies of motion capture point data
"""
from .plot import create_joint_frame
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def update_elements(num, positions, ax, joint_graph, joint_names):
    """
    """
    if num % 500 == 0:
        print('processing frame: ', num)

    # extract joint positions to plot
    joints = positions.iloc[num]

    # plot the joints
    ax.clear()
    updated_elements = create_joint_frame(ax, joints, joint_graph, joint_names)
    ax.set_xlim3d([-70, 30])
    ax.set_ylim3d([-50, 50])
    ax.set_zlim3d([100, 200])

    # extract experiment response information for this time
    # the first response where response time is greater than this joint time
    # is the response block/trial we are in
    time = joints[0]

    title = 'Time: %d' % time

    ax.set_title(title)
    ax.view_init(-90, 90)
    return updated_elements


def render_animation(time_df, joint_graph, joint_names, figsize=(10,10)):
    """
    """
    # start by plotting the first frame
    joints = time_df.iloc[0]
    num_frames, _ = time_df.shape

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(projection="3d")
    elements = create_joint_frame(ax, joints, joint_graph, joint_names)

    # set view limits and positon
    # TODO: these will need to be discovered or parameterized?
    ax.set_xlim3d([-70, 30])
    ax.set_ylim3d([-50, 50])
    ax.set_zlim3d([100, 200])
    ax.view_init(-90, 90)

    # create animation object
    # TODO: probably need to set/calculate interval as well not hardcode
    ani = animation.FuncAnimation(
        fig, update_elements, num_frames,
        fargs=(time_df, ax, joint_graph, joint_names), interval=50)

    return ani
