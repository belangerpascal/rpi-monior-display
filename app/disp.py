import sys
import psutil
import board
import digitalio
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from adafruit_rgb_display.st7789 import ST7789
from collections import deque
from gpiozero import Device

# User Config
REFRESH_RATE = 0.05
HIST_SIZE = 61
PLOT_CONFIG = [
    {
        'title': 'LOAD',
        'ylim': (0, 100),
        'line_config': [
            {'color': (0, 0, 255), 'width': 2},
            {'color': (0, 96, 255), 'width': 2},
            {'color': (0, 255, 96), 'width': 2},
            {'color': (96, 255, 0), 'width': 2},
        ]
    },
    {
        'title': 'TEMP',
        'ylim': (20, 50),
        'line_config': [
            {'color': (255, 0, 0), 'width': 2},
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

# Create an image buffer
image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)

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
    # Clear the image
    draw.rectangle([(0, 0), image.size], fill=(0, 0, 0))

    # Update lines with the latest data
    for plot, config in enumerate(PLOT_CONFIG):
        for index, line_config in enumerate(config['line_config']):
            data = y_data[plot][index]
            if None not in data:
                avg_data = sum(data) / len(data)
                color = line_config['color']
                width = line_config['width']
                points = [(x_time[i], avg_data) for i in range(len(x_time))]
                draw.line(points, fill=color, width=width)

    # Display the updated image
    disp.image(image)

try:
    print("Looping")
    while True:
        update_data()
        update_plot()
        sys.stdout.flush()
except KeyboardInterrupt:
    print("Loop interrupted by user.")
finally:
    if Device.pin_factory is not None:
        Device.pin_factory.reset()
    print("Exiting program.")
