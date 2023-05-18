"""Plot functions

Functions to plot a single frame of joint positions on a 3D canvas/axis
"""
import matplotlib.pyplot as plt


def joint_symbol_lists(joint_names):
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
    x_joints = ['%sX' % name for name in joint_names]
    y_joints = ['%sY' % name for name in joint_names]
    z_joints = ['%sZ' % name for name in joint_names]

    return x_joints, y_joints, z_joints
    
def create_joint_frame(ax, joints, joint_graph, joint_names):
    """Given a 3D ax in a figure, plot the given joint/skeleton
    points in the figure axis.

    Parameters
    ----------
    ax - a 3D matplotlib axis on which to plot the joint positions
    joints - A Pandas series or dictionary like object with joint positions
       as features or keys of the expected names.
    joint_graph - The directed graph of the skeleton/connections that defines
       the joint relationships.
    joint_names - The symbolic names of the joints in the joint graph

    Returns
    -------
    fig_elements - A list of line figure elements are returned
    Implicitly  the joints are plotted on the given figure
    """
    x_joints, y_joints, z_joints = joint_symbol_lists(joint_names)

     # pull out the x,y and z positions by joint names
    x_pos = joints[x_joints]
    y_pos = joints[y_joints]
    z_pos = joints[z_joints]

    # first scatter plot the joint positions as blue circle markers
    #fig_elements = ax.scatter(x_pos, y_pos, z_pos, 'bo')[0]
    fig_elements = [ax.plot(x, y, z, 'bo')[0] for x,y,z in zip(x_pos, y_pos, z_pos)] 
    
    # now plot the joint skeleton graph as red lines between joint positions
    for src, dst in joint_graph:
        line = ax.plot([x_pos[src], x_pos[dst]],
                      [y_pos[src], y_pos[dst]],
                      [z_pos[src], z_pos[dst]],
                      'r')[0]
        fig_elements.append(line)
        
    return fig_elements

def plot_joint_frame(joints, joint_graph, joint_names, figsize=(10,10)):
    """Given the joint positions at a point in time, render their
    joints and the joint graph on a 3D canvas.

    Parameters
    ----------
    joints - A Pandas series or dictionary like object with joint positions
       as features or keys of the expected names.
    joint_graph - The directed graph of the skeleton/connections that defines
       the joint relationships.
    joint_names - The symbolic names of the joints in the joint graph
    figsize - default figure size is (10, 10) inches, can be overridden.

    Returns
    -------
    fig - This function creates and returns a matplotlib figure object
       that can be displayed or saved as a single frame image.
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(projection="3d")
    _ = create_joint_frame(ax, joints, joint_graph, joint_names)
    return fig

