import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button
import numpy as np
import signal

# if you are having difficulty with the graphics,
# try using one of the following backends.
import matplotlib
matplotlib.use('tkagg')  # requires TkInter


class ACMotorAnimation:
    def __init__(self, stator_radius=1.0, rotor_radius=0.6, shaft_radius=0.15):
        """
        Initialize AC Motor animation
        
        Parameters:
        -----------
        stator_radius : float
            Outer radius of the stator
        rotor_radius : float
            Outer radius of the rotor
        shaft_radius : float
            Radius of the motor shaft
        """
        # Used to indicate initialization
        self.flagInit = True
        
        # Motor dimensions
        self.stator_radius = stator_radius
        self.rotor_radius = rotor_radius
        self.shaft_radius = shaft_radius
        
        # Initializes a figure and axes object
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        
        # Initializes a list object that will be used to contain
        # handles to the patches and line objects.
        self.handle = []
        
        # Set axis limits
        limit = 1.5 * stator_radius
        plt.axis([-limit, limit, -limit, limit])
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('AC Motor Visualization')

        # Create exit button
        self.button_ax = plt.axes([0.8, 0.805, 0.1, 0.075])
        self.exit_button = Button(self.button_ax, label='Exit', color='r')
        self.exit_button.label.set_fontweight('bold')
        self.exit_button.label.set_fontsize(18)
        self.exit_button.on_clicked(lambda event: exit())

        # Register <ctrl+c> signal handler to stop the simulation
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def update(self, theta, omega=None, torque=None):
        """
        Update the motor animation
        
        Parameters:
        -----------
        theta : float
            Rotor angle in radians
        omega : float, optional
            Angular velocity in rad/s (for display)
        torque : float, optional
            Motor torque in N-m (for display)
        """
        self.drawStator()
        self.drawRotor(theta)
        self.drawShaft(theta)
        
        # Update title with motor state if provided
        if omega is not None and torque is not None:
            self.ax.set_title(f'AC Motor: θ={theta:.2f} rad, ω={omega:.2f} rad/s, τ={torque:.2f} N-m')
        elif omega is not None:
            self.ax.set_title(f'AC Motor: θ={theta:.2f} rad, ω={omega:.2f} rad/s')
        else:
            self.ax.set_title(f'AC Motor: θ={theta:.2f} rad')
        
        # After each function has been called, initialization is over
        if self.flagInit:
            self.flagInit = False

    def drawStator(self):
        """Draw the stationary stator with windings"""
        # Outer stator casing
        stator_outer = plt.Circle((0, 0), self.stator_radius, 
                                  color='gray', fill=True, alpha=0.3,
                                  edgecolor='black', linewidth=2)
        
        # Inner stator boundary
        stator_inner = plt.Circle((0, 0), self.rotor_radius + 0.05,
                                  color='white', fill=True,
                                  edgecolor='black', linewidth=1)
        
        if self.flagInit:
            self.handle.append(stator_outer)
            self.handle.append(stator_inner)
            self.ax.add_patch(self.handle[0])
            self.ax.add_patch(self.handle[1])
            
            # Draw stator windings (fixed positions)
            # 6 stator poles (3-phase motor)
            for i in range(6):
                angle = i * np.pi / 3
                x = (self.stator_radius - 0.15) * np.cos(angle)
                y = (self.stator_radius - 0.15) * np.sin(angle)
                
                # Winding coil representation
                coil = plt.Circle((x, y), 0.08, 
                                 color=['red', 'yellow', 'blue'][i % 3],
                                 alpha=0.7, edgecolor='black', linewidth=1)
                self.handle.append(coil)
                self.ax.add_patch(self.handle[-1])

    def drawRotor(self, theta):
        """Draw the rotating rotor with bars"""
        # Main rotor body
        rotor_body = plt.Circle((0, 0), self.rotor_radius,
                               color='lightblue', fill=True, alpha=0.6,
                               edgecolor='black', linewidth=2)
        
        if self.flagInit:
            self.handle.append(rotor_body)
            self.ax.add_patch(self.handle[-1])
            
            # Create rotor bars (squirrel cage representation)
            # 8 rotor bars
            self.rotor_bar_handles = []
            for i in range(8):
                line_handle, = self.ax.plot([], [], 'k-', linewidth=3)
                self.rotor_bar_handles.append(line_handle)
                self.handle.append(line_handle)
        
        # Update rotor bars based on theta
        for i, line_handle in enumerate(self.rotor_bar_handles):
            angle = theta + i * 2 * np.pi / 8
            r_inner = self.shaft_radius + 0.05
            r_outer = self.rotor_radius - 0.05
            
            x = [r_inner * np.cos(angle), r_outer * np.cos(angle)]
            y = [r_inner * np.sin(angle), r_outer * np.sin(angle)]
            
            line_handle.set_data(x, y)

    def drawShaft(self, theta):
        """Draw the motor shaft with a reference mark"""
        # Main shaft
        shaft = plt.Circle((0, 0), self.shaft_radius,
                          color='darkgray', fill=True,
                          edgecolor='black', linewidth=2)
        
        if self.flagInit:
            self.handle.append(shaft)
            self.ax.add_patch(self.handle[-1])
            
            # Reference mark on shaft (to show rotation)
            self.ref_mark, = self.ax.plot([], [], 'r-', linewidth=3)
            self.handle.append(self.ref_mark)
        
        # Update reference mark
        x = [0, self.shaft_radius * np.cos(theta)]
        y = [0, self.shaft_radius * np.sin(theta)]
        self.ref_mark.set_data(x, y)


# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Create animation object
    anim = ACMotorAnimation(stator_radius=1.0, rotor_radius=0.6, shaft_radius=0.15)
    
    # Simulation parameters
    dt = 0.05  # time step
    t = 0
    theta = 0
    omega = 2.0  # angular velocity (rad/s)
    
    plt.ion()  # Turn on interactive mode
    plt.show()
    
    # Animation loop
    try:
        while True:
            # Update motor state
            theta += omega * dt
            torque = 5.0 * np.sin(2 * t)  # Example varying torque
            
            # Update animation
            anim.update(theta, omega, torque)
            
            # Redraw
            plt.pause(dt)
            
            # Update time
            t += dt
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
        plt.close()