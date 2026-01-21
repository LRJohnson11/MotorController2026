import matplotlib.pyplot as plt 
from matplotlib.lines import Line2D
import numpy as np

plt.ion()  # enable interactive drawing


class MotorDataPlotter:
    """
    Flexible data plotter for motor control variables.
    Easily scalable - just modify the plot_config list to add/remove plots.
    """
    
    def __init__(self, plot_config=None):
        """
        Initialize the motor data plotter.
        
        Parameters:
        -----------
        plot_config : list of dict, optional
            List of plot configurations. Each dict should contain:
            - 'signals': list of signal names to plot
            - 'ylabel': y-axis label
            - 'xlabel': x-axis label (optional, only for last plot)
            - 'title': plot title (optional, only for first plot)
            - 'legend': list of legend labels (optional)
            - 'conversion': conversion factor (optional, default=1.0)
            
            If None, uses default motor configuration.
        """
        
        # Default configuration for typical motor control
        if plot_config is None:
            self.plot_config = [
                {
                    'signals': ['theta_ref', 'theta'],
                    'ylabel': 'Angle (deg)',
                    'title': 'AC Motor Data',
                    'legend': ['Reference', 'Actual'],
                    'conversion': 180.0/np.pi  # rad to deg
                },
                {
                    'signals': ['omega'],
                    'ylabel': 'Velocity (rad/s)',
                },
                {
                    'signals': ['current_d', 'current_q'],
                    'ylabel': 'Current (A)',
                    'legend': ['I_d', 'I_q']
                },
                {
                    'signals': ['torque'],
                    'ylabel': 'Torque (N-m)',
                    'xlabel': 't (s)'
                }
            ]
        else:
            self.plot_config = plot_config
        
        # Number of subplots
        self.num_plots = len(self.plot_config)
        
        # Create figure and axes handles
        self.fig, self.ax = plt.subplots(self.num_plots, 1, sharex=True, figsize=(10, 2.5*self.num_plots))
        
        # Handle single subplot case
        if self.num_plots == 1:
            self.ax = [self.ax]
        
        # Initialize data histories
        self.time_history = []
        self.data_histories = {}
        
        # Initialize all signal histories based on config
        for plot in self.plot_config:
            for signal in plot['signals']:
                self.data_histories[signal] = []
        
        # Create subplot handles
        self.handle = []
        for i, plot in enumerate(self.plot_config):
            self.handle.append(
                myPlot(
                    self.ax[i],
                    xlabel=plot.get('xlabel', ''),
                    ylabel=plot.get('ylabel', ''),
                    title=plot.get('title', ''),
                    legend=plot.get('legend', None)
                )
            )
    
    def update(self, t: float, **kwargs):
        """
        Update all plots with new data.
        
        Parameters:
        -----------
        t : float
            Current time
        **kwargs : dict
            Signal values as keyword arguments. 
            Example: theta=1.5, omega=2.0, torque=3.5
        """
        # Update time history
        self.time_history.append(t)
        
        # Update each signal's history
        for signal_name, value in kwargs.items():
            if signal_name in self.data_histories:
                self.data_histories[signal_name].append(value)
        
        # Update each plot
        for i, plot in enumerate(self.plot_config):
            # Get data for this plot
            plot_data = []
            conversion = plot.get('conversion', 1.0)
            
            for signal in plot['signals']:
                if signal in self.data_histories:
                    # Apply conversion factor (e.g., rad to deg)
                    converted_data = [val * conversion for val in self.data_histories[signal]]
                    plot_data.append(converted_data)
                else:
                    # If signal not provided, append empty list
                    plot_data.append([])
            
            # Update the plot
            self.handle[i].update(self.time_history, plot_data)


class myPlot:
    """ 
    Create each individual subplot.
    """
    def __init__(self, ax,
                 xlabel='',
                 ylabel='',
                 title='',
                 legend=None):
        """ 
        ax - This is a handle to the axes of the figure
        xlabel - Label of the x-axis
        ylabel - Label of the y-axis
        title - Plot title
        legend - A tuple of strings that identify the data. 
                 EX: ("data1","data2", ... , "dataN")
        """
        self.legend = legend
        self.ax = ax                  # Axes handle
        self.colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        # A list of colors. The first color in the list corresponds
        # to the first line object, etc.
        # 'b' - blue, 'g' - green, 'r' - red, 'c' - cyan, 'm' - magenta
        # 'y' - yellow, 'k' - black
        self.line_styles = ['-', '-', '--', '-.', ':']
        # A list of line styles.  The first line style in the list
        # corresponds to the first line object.
        # '-' solid, '--' dashed, '-.' dash_dot, ':' dotted

        self.line = []

        # Configure the axes
        self.ax.set_ylabel(ylabel)
        self.ax.set_xlabel(xlabel)
        self.ax.set_title(title)
        self.ax.grid(True)

        # Keeps track of initialization
        self.init = True   

    def update(self, time, data):
        """ 
        Adds data to the plot.  
        time is a list, 
        data is a list of lists, each list corresponding to a line on the plot
        """
        if self.init == True:  # Initialize the plot the first time routine is called
            for i in range(len(data)):
                # Instantiate line object and add it to the axes
                self.line.append(Line2D(time,
                                        data[i],
                                        color=self.colors[np.mod(i, len(self.colors))],
                                        ls=self.line_styles[np.mod(i, len(self.line_styles))],
                                        label=self.legend[i] if self.legend is not None else None))
                self.ax.add_line(self.line[i])
            self.init = False
            # add legend if one is specified
            if self.legend is not None:
                self.ax.legend(handles=self.line)
        else:  # Add new data to the plot
            # Updates the x and y data of each line.
            for i in range(len(self.line)):
                self.line[i].set_xdata(time)
                self.line[i].set_ydata(data[i])

        # Adjusts the axis to fit all of the data
        self.ax.relim()
        self.ax.autoscale()


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    import time
    
    # Example 1: Using default motor configuration
    print("Example 1: Default motor configuration")
    plotter1 = MotorDataPlotter()
    
    # Simulate motor operation
    for i in range(100):
        t = i * 0.01
        theta_ref = np.pi/4 * np.sin(0.5 * t)
        theta = theta_ref + 0.1 * np.sin(5 * t)
        omega = 0.5 * np.pi/4 * np.cos(0.5 * t)
        current_d = 2.0 + 0.5 * np.sin(t)
        current_q = 3.0 + 0.8 * np.cos(t)
        torque = 5.0 * np.sin(t)
        
        plotter1.update(
            t=t,
            theta_ref=theta_ref,
            theta=theta,
            omega=omega,
            current_d=current_d,
            current_q=current_q,
            torque=torque
        )
        
        plt.pause(0.001)
    
    # Example 2: Custom configuration
    print("\nExample 2: Custom configuration for different motor application")
    
    custom_config = [
        {
            'signals': ['position_ref', 'position'],
            'ylabel': 'Position (m)',
            'title': 'Linear Motor Data',
            'legend': ['Ref', 'Actual']
        },
        {
            'signals': ['velocity'],
            'ylabel': 'Velocity (m/s)',
        },
        {
            'signals': ['voltage_a', 'voltage_b', 'voltage_c'],
            'ylabel': 'Phase Voltage (V)',
            'legend': ['V_a', 'V_b', 'V_c']
        },
        {
            'signals': ['force'],
            'ylabel': 'Force (N)',
            'xlabel': 'Time (s)'
        }
    ]
    
    plotter2 = MotorDataPlotter(plot_config=custom_config)
    
    # Simulate different motor
    for i in range(100):
        t = i * 0.01
        
        plotter2.update(
            t=t,
            position_ref=0.5 * t,
            position=0.5 * t + 0.01 * np.sin(10 * t),
            velocity=0.5 + 0.1 * np.cos(10 * t),
            voltage_a=120 * np.sin(2 * np.pi * 60 * t),
            voltage_b=120 * np.sin(2 * np.pi * 60 * t - 2*np.pi/3),
            voltage_c=120 * np.sin(2 * np.pi * 60 * t + 2*np.pi/3),
            force=100 + 20 * np.sin(t)
        )
        
        plt.pause(0.001)
    
    print("\nPlotting complete. Close windows to exit.")
    plt.show(block=True)