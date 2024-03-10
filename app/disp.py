from collections import deque
import sys
import psutil
import board
import digitalio
from adafruit_rgb_display.st7789 import ST7789
import matplotlib.pyplot as plt
from PIL import Image
from gpiozero import Device

# User Config
REFRESH_RATE = 0.05
HIST_SIZE = 61
PLOT_CONFIG = [
    {
        'title': 'LOAD',
        'ylim': (0, 100),
        'line_config': [
            {'color': '#0000FF', 'width': 2},
            {'color': '#0060FF', 'width': 2},
            {'color': '#00FF60', 'width': 2},
            {'color': '#60FF00', 'width': 2},
        ]
    },
    {
        'title': 'TEMP',
        'ylim': (20, 50),
        'line_config': [
            {'color': '#FF0000', 'width': 2},
        ]
    }
]

CPU_COUNT = len(psutil.cpu_percent(interval=REFRESH_RATE, percpu=True))

# Setup X data storage
x_time = [x * REFRESH_RATE for x in range(HIST_SIZE)]
x_time.reverse()

# Setup Y data storage
y_data = [
    [deque([None] * HIST_SIZE, maxlen=HIST_SIZE) for _ in plot['line_config']]
    for plot in PLOT_CONFIG
]

# Setup display
disp = ST7789(
    board.SPI(),
    height=240,
    width=280,
    y_offset=20,
    rotation=90,
    baudrate=40000000,
    cs=digitalio.DigitalInOut(board.CE0),
    dc=digitalio.DigitalInOut(board.D25),
    rst=digitalio.DigitalInOut(board.D27)
)

# Setup plot figure
plt.style.use('dark_background')
fig, ax = plt.subplots(2, 1, figsize=(disp.width / 100, disp.height / 100))

# Setup plot axis
ax[0].xaxis.set_ticklabels([])
for plot, a in enumerate(ax):
    # Add grid to all plots
    a.grid(True, linestyle=':')
    # Limit and invert x time axis
    a.set_xlim(min(x_time), max(x_time))
    a.invert_xaxis()
    # Custom settings
    if 'title' in PLOT_CONFIG[plot]:
        a.set_title(PLOT_CONFIG[plot]['title'], position=(0.5, 0.8))
    if 'ylim' in PLOT_CONFIG[plot]:
        a.set_ylim(PLOT_CONFIG[plot]['ylim'])

# Setup plot lines
plot_lines = []
for plot, config in enumerate(PLOT_CONFIG):
    lines = []
    for index, line_config in enumerate(config['line_config']):
        # create line
        line, = ax[plot].plot(x_time, y_data[plot][index])
        # custom settings
        if 'color' in line_config:
            line.set_color(line_config['color'])
        if 'width' in line_config:
            line.set_linewidth(line_config['width'])
        if 'style' in line_config:
            line.set_linestyle(line_config['style'])
        # add line to list
        lines.append(line)
    plot_lines.append(lines)

def update_data():
    # Update data
    cpu_percs = psutil.cpu_percent(interval=REFRESH_RATE, percpu=True)
    y_data[0].append(cpu_percs)

    cpu_temps = [shwtemp.current for shwtemp in psutil.sensors_temperatures().get('cpu_thermal', [])]
    y_data[1].append(cpu_temps)

    # Print statements for debugging
    print(f"CPU Percentages: {cpu_percs}")
    print(f"CPU Temperatures: {cpu_temps}")

    # Check if data is within y-axis limits
    for plot, limits in enumerate(PLOT_CONFIG):
        if 'ylim' in limits:
            for index, data_point in enumerate(cpu_percs if plot == 0 else cpu_temps):
                limit_min, limit_max = limits['ylim']
                if not (limit_min <= float(data_point) <= limit_max):
                    print(f"Warning: Data point {data_point} is outside the y-axis limits for Plot {plot + 1}, Line {index + 1}")
                    print(f"Y-axis limits: {limit_min} to {limit_max}")

def update_plot():
    # update lines with the latest data
    for plot, lines in enumerate(plot_lines):
        for index, line in enumerate(lines):
            line.set_ydata(y_data[plot][index])
    # draw the plots
    canvas = plt.get_current_fig_manager().canvas
    plt.tight_layout()
    canvas.draw()
    # transfer into PIL image
    image = Image.frombytes('RGBA', canvas.get_width_height(), canvas.buffer_rgba())

    # Ensure the image does not exceed display dimensions
    if image.width > disp.width or image.height > disp.height:
        image = image.resize((disp.width, disp.height))

    # display the image
    disp.image(image)

    # update the plot after displaying the image
    for plot, lines in enumerate(plot_lines):
        for index, line in enumerate(lines):
            line.set_ydata(y_data[plot][index])
        # autoscale if not specified
        if 'ylim' not in PLOT_CONFIG[plot].keys():
            ax[plot].relim()
            ax[plot].autoscale_view()
    plt.draw()
    print("Plot Updated")



try:
    print("Looping")
    while True:
        update_data()
        update_plot()
        sys.stdout.flush()  # Moved it here
except KeyboardInterrupt:
    print("Loop interrupted by user.")
finally:
    if Device.pin_factory is not None:
        Device.pin_factory.reset()
    print("Exiting program.")