import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image
import board
import digitalio
from adafruit_rgb_display import st7789

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(2.8, 2.4))

# Set up the display
disp = st7789.ST7789(board.SPI(), height=280, width=240, y_offset=20, rotation=0,
                     baudrate=40000000,
                     cs=digitalio.DigitalInOut(board.CE0),
                     dc=digitalio.DigitalInOut(board.D25),
                     rst=digitalio.DigitalInOut(board.D27)
)

# Number of stars in the field
num_stars = 100

# Generate random positions for stars
x = np.random.rand(num_stars)
y = np.random.rand(num_stars)

# Gradually change intensities for stars (fade in and fade out)
fade_speed = 0.002
intensities = np.clip(np.random.uniform(0.5, 1.0, size=num_stars) - np.arange(num_stars) * fade_speed, 0, 1)

# Reduce the displacement for subtlety
displacement = 0.001
x += np.random.uniform(-displacement, displacement, size=num_stars)
y += np.random.uniform(-displacement, displacement, size=num_stars)

# Function to initialize the plot
def init():
    ax.clear()
    ax.set_facecolor('k')  # Set background color to black
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return ax,

# Function to update the animation frame
def update(frame):
    ax.clear()
    ax.set_facecolor('k')  # Set background color to black
    ax.scatter(x, y, s=1, c='white', alpha=intensities)

# Create the animation
animation = FuncAnimation(fig, update, init_func=init, frames=None, interval=1000 / 5, repeat=True)

# Show the animation
plt.tight_layout()
plt.show()
