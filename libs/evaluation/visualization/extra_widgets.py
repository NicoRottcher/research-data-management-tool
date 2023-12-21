"""
Scripts for standard widgtes used within interactive tools
Created in 2023
@author: Nico Röttcher
"""

from ipywidgets import *

from evaluation.visualization import plot


def button_autoscale(description, ax, which="y", margin=0.05, lines=None, **kwargs):
    """
    Add an axis autoscale button.
    :param description: str
        description of the button
    :param ax: matplotlib.Axes
        Axes object which should be autoscaled
    :param which: str one of ['y, 'x']
        which axis to scale
    :param margin: float, optonal, default=0.05
        percentage of margin considered during autoscale, default 5%
    :param lines: list of matplotlib.lines or None
        list of lines which should be scaled,
        if None scale all lines in axis
    :param kwargs:
        keyword arguments of widgets.Button()
    :return: widgets.Button object
    """

    def on_button_autoscale(changed_value):
        plot.autoscale_axis(ax, which=which, margin=margin, lines=lines)
        ax.get_figure().canvas.draw()

    widget_button_autoscale = widgets.Button(
        description=description,
        **kwargs
    )
    widget_button_autoscale.on_click(on_button_autoscale)
    return widget_button_autoscale
