from collections import deque
import psutil
# Blinka CircuitPython
import board
import digitalio
from adafruit_rgb_display import st7789
# Matplotlib
import matplotlib.pyplot as plt
# Python Imaging Library
from PIL import Image
import time

#pylint: disable=bad-continuation
#==| User Config |========================================================
REFRESH_RATE = 1
HIST_SIZE = 61
PLOT_CONFIG = (
    #--------------------
    # PLOT 1 (upper plot)
    #--------------------
    {
    'title' : 'LOAD',
    'ylim' : (0, 100),
    'line_config' : (
        {'color' : '#0000FF', 'width' : 2},
        {'color' : '#0060FF', 'width' : 2},
        {'color' : '#00FF60', 'width' : 2},
        {'color' : '#60FF00', 'width' : 2},
        )
    },
    #--------------------
    # PLOT 2 (lower plot)
    #--------------------
    {
    'title' : 'TEMP',
    'ylim' : (20, 50),
    'line_config' : (
        {'color' : '#FF0000', 'width' : 2},
        )
    }
)

CPU_COUNT = 1

def update_data():
    ''' Do whatever to update your data here. General form is:
           y_data[plot][line].append(new_data_point)
    '''
    cpu_percs = psutil.cpu_percent(interval=REFRESH_RATE, percpu=True)
    print(cpu_percs)
    y_data[0].append(cpu_percs)

    cpu_temps = []
    for shwtemp in psutil.sensors_temperatures()['cpu_thermal']:
        cpu_temps.append(shwtemp.current)
    print(cpu_temps)
    y_data[1].append(cpu_temps)

#==| User Config |========================================================
#pylint: enable=bad-continuation

# Setup X data storage
x_time = [x * REFRESH_RATE for x in range(HIST_SIZE)]
x_time.reverse()

# Setup Y data storage
y_data = [ [deque([None] * HIST_SIZE, maxlen=HIST_SIZE) for _ in plot['line_config']]
           for plot in PLOT_CONFIG
         ]

# Setup display
disp = st7789.ST7789(board.SPI(), height=280, width=240, y_offset=20, rotation=0,
                     baudrate=40000000,
                     cs=digitalio.DigitalInOut(board.CE0),
                     dc=digitalio.DigitalInOut(board.D25),
                     rst=digitalio.DigitalInOut(board.D27))

# Setup plot figure
plt.style.use('dark_background')
fig, ax = plt.subplots(2, 1, figsize=(disp.width / 100, disp.height / 100))

# Setup plot axis
ax[0].xaxis.set_ticklabels([])
for plot, a in enumerate(ax):
    # add grid to all plots
    a.grid(True, linestyle=':')
    # limit and invert x time axis
    a.set_xlim(min(x_time), max(x_time))
    a.invert_xaxis()
    # custom settings
    if 'title' in PLOT_CONFIG[plot]:
        a.set_title(PLOT_CONFIG[plot]['title'], position=(0.5, 0.8))
    if 'ylim' in PLOT_CONFIG[plot]:
        a.set_ylim(PLOT_CONFIG[plot]['ylim'])

# Setup plot lines
#pylint: disable=redefined-outer-name
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

def update_plot():
    # update lines with latest data
    for plot, lines in enumerate(plot_lines):
        for index, line in enumerate(lines):
            line.set_ydata(y_data[plot][index])
        # autoscale if not specified
        if 'ylim' not in PLOT_CONFIG[plot].keys():
            ax[plot].relim()
            ax[plot].autoscale_view()
    # draw the plots
    canvas = plt.get_current_fig_manager().canvas
    plt.tight_layout()
    canvas.draw()
    # transfer into PIL image and display
    image = Image.frombytes('RGB', canvas.get_width_height(),
                            canvas.tostring_rgb())
    disp.image(image)

MAX_ITERATIONS = 1000
iteration_count = 0

print("looping")
while iteration_count < MAX_ITERATIONS:
    update_data()
    update_plot()
    iteration_count += 1
    # Add a delay to control the update rate
    time.sleep(REFRESH_RATE)

print("Max iterations reached. Exiting loop.")