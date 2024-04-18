from collections import deque
import os
import sys
import psutil
import board
import digitalio
from adafruit_rgb_display.st7789 import ST7789
import matplotlib.pyplot as plt
plt.style.use('ggplot')  # Use the 'ggplot' style
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Device, Button
import time
import socket
import platform
import docker
dockerClient = docker.DockerClient()

# Load your images
disk_active_image = Image.open('./b-square-active-240.png')
disk_idle_image = Image.open('./b-square-idle-240.png')

scroll_pos = 0

# Setup GPIO pin 3 as an input
pin7 = Button(4)

button_state = 0

# Turn on the Backlight
backlight = digitalio.DigitalInOut(board.D12)
backlight.switch_to_output()
backlight.value = False

# User Config
REFRESH_RATE = 0.033
HIST_SIZE = 61
px = 1/plt.rcParams['figure.dpi']
CPU_COUNT = psutil.cpu_count()

# Initialize previous disk activity counters
prev_disk_activity = psutil.disk_io_counters()

PLOT_CONFIG_LOAD = [
    {
        'title': 'LOAD',
        'ylim': (0, 100),
        'line_config': [{'color': '#0000FF', 'width': .5}] * CPU_COUNT,
    },
]

PLOT_CONFIG_TEMP = [
    {
        'title': 'TEMP',
        'ylim': (0, 100),  # Adjust this range according to your CPU's temperature range
        'line_config': [{'color': '#FF0000', 'width': .5}],
    },
]

# Setup X data storage
x_time = [x * REFRESH_RATE for x in range(HIST_SIZE)]
x_time.reverse()

# Setup Y data storage
y_data_load = [
    [deque([None] * HIST_SIZE, maxlen=HIST_SIZE) for _ in plot['line_config']]
    for plot in PLOT_CONFIG_LOAD
]

y_data_temp = [
    [deque([None] * HIST_SIZE, maxlen=HIST_SIZE) for _ in plot['line_config']]
    for plot in PLOT_CONFIG_TEMP
]
# Setup display
disp = ST7789(board.SPI(), height=280, width=280, y_offset=20, rotation=90,
                     baudrate=40000000,
                     cs=digitalio.DigitalInOut(board.CE0),
                     dc=digitalio.DigitalInOut(board.D25),
                     rst=digitalio.DigitalInOut(board.D27))

# Setup plot figure
#plt.style.use('ggplot')  # Use the 'ggplot' style
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(280*px, 240*px))

ax.xaxis.set_ticklabels([])
ax.set_xlim(min(x_time), max(x_time))
ax.invert_xaxis()
ax.grid(True, color='black')  # Set the grid lines to black
ax.set_facecolor('#333333')  # Set the axes background to charcoal grey
ax.tick_params(colors='white')  # Set the color of the tick labels to white


# Create a second buffer for double buffering
buffer1 = Image.new('RGB', (280, 240))
buffer2 = Image.new('RGB', (280, 240))
draw1 = ImageDraw.Draw(buffer1)
draw2 = ImageDraw.Draw(buffer2)

def getContainers():
    containersReturn = []
    containers = dockerClient.containers.list()
    for container in containers:
        if ("ceph" not in container.name):
          containersReturn.append(container.name.split(".", 1)[0])
    return containersReturn

def update_data_load():
    cpu_percs = psutil.cpu_percent(interval=REFRESH_RATE, percpu=True)
    for cpu in range(CPU_COUNT):
        y_data_load[0][cpu].append(cpu_percs[cpu])

def update_data_temp():
    cpu_temps = [shwtemp.current for shwtemp in psutil.sensors_temperatures().get('cpu_thermal', [])]
    y_data_temp[0][0].append(sum(cpu_temps) / len(cpu_temps) if cpu_temps else 0)

def display_system_info(draw):
    global scroll_pos  # Add this line to use the global variable

    # Get the hostname
    hostname = socket.gethostname()

    # Get the IP address
    ip_address = socket.gethostbyname(hostname)

    # Get the OS name and version
    os_name = platform.system()
    os_version = platform.release()

    # Get the CPU percentage
    cpu_percs = psutil.cpu_percent(interval=REFRESH_RATE)

    #Get the load (1,5,15)
    load_tuple = [round(x,2) for x in psutil.getloadavg()]

    #Get running containers
    containers = getContainers()

    # Calculate the total height of the container list
    total_height = len(containers) * 20  # Adjust this value as needed to change the line spacing

    # Only start scrolling if the total height exceeds 150 pixels
    if total_height > 150:
        # Update the scroll position
        scroll_pos += 20  # Adjust this value as needed to change the scroll speed

        # If the scroll position is greater than the total height of the text, reset it
        if scroll_pos > total_height:
            scroll_pos = 0

    # Clear the buffer
    draw.rectangle((0, 0, 280, 240), fill=(0, 0, 0))

    # Set the text color
    text_color = (40,254,20)

    # Set the font size
    font = ImageFont.truetype("/usr/share/fonts/opentype/courier-prime/Courier Prime Bold.otf", 16)

    # Draw the information on the buffer
    draw.text((10, 10), f"{hostname} CPU Usage: {cpu_percs}", fill=text_color, font=font)
    draw.text((10, 30), f"Load: {load_tuple}", fill=text_color, font=font)
    draw.text((10, 50), f"IP Address: {ip_address}", fill=text_color, font=font)
    draw.text((10, 70), f"OS Version: {os_version}", fill=text_color, font=font)

      # Draw each container on a new line, offset by the scroll position
    y = 90  # Adjust this value as needed to change the starting position
    for i in range(len(containers)):
        # Calculate the index of the container to display
        index = (i + scroll_pos // 20) % len(containers)
        if 90 <= y <= 240:  # Only draw the text if it's within these y-coordinates
            draw.text((10, y), f"{containers[index]}", fill=text_color, font=font)
        y += 20  # Adjust this value as needed to change the line spacing

    # Display the buffer
    disp.image(buffer1)

def update_data_disk():
    global draw1, draw2, buffer1, buffer2, prev_disk_activity

    # Redefine draw1 and draw2 after swapping buffers
    draw1, draw2 = draw2, draw1
    buffer1, buffer2 = buffer2, buffer1
    draw1 = ImageDraw.Draw(buffer1)

    # Get the current disk activity
    disk_activity = psutil.disk_io_counters()

    # Clear the buffer
    draw1.rectangle((0, 0, 280, 240), fill=(0, 0, 0))

    # If the disk is active, display the active image
    if disk_activity.read_count > prev_disk_activity.read_count or disk_activity.write_count > prev_disk_activity.write_count:
        # Resize the image to 50x50 pixels
        small_active_image = disk_active_image.resize((50, 50))
        # Display the image in the bottom right corner
        buffer1.paste(small_active_image, (210, 170))
        # Turn on the backlight
        backlight.value = True
    else:
        # If the disk is idle, turn off the backlight
        backlight.value = False

    # Display the buffer
    disp.image(buffer1)

    # Update the previous disk activity counters
    prev_disk_activity = disk_activity
    backlight.value = False

def update_plot():
    global draw1, draw2, buffer1, buffer2, button_state
    # Redefine draw1 and draw2 after swapping buffers
    draw1, draw2 = draw2, draw1
    buffer1, buffer2 = buffer2, buffer1
    draw1 = ImageDraw.Draw(buffer1)

    # Check the state of GPIO pin 7
    if pin7.is_pressed:  # is_pressed is True when the pin reads low
        # If pin 7 is Low, toggle the button state
        print("Button Pressed")
        button_state = (button_state + 1) % 4  # This will cycle between 0, 1, and 2
        time.sleep(0.5)  # Debounce the button press

    if button_state == 0:
        update_data_disk()
        disp.image(buffer1)
    elif button_state == 1:
        display_system_info(draw1)
        disp.image(buffer1)
    elif button_state == 2:
        # Clear the plot
        ax.clear()
        ax.plot(x_time, y_data_load[0][0], linewidth=2, color='#0000FF')
        ax.set_ylim(PLOT_CONFIG_LOAD[0]['ylim'])
        ax.set_title(PLOT_CONFIG_LOAD[0]['title'], position=(0.5, 0.8), color='white')
        fig.canvas.draw()  # Draw the figure using the Agg backend
        image = Image.frombytes('RGB', fig.canvas.get_width_height(),
                                fig.canvas.tostring_rgb()).convert('RGB')
        draw1.rectangle((0, 0, 280, 240), fill=(0, 0, 0))
        buffer1.paste(image)
        disp.image(buffer1)
    elif button_state == 3:
        # Clear the plot
        ax.clear()
        ax.plot(x_time, y_data_temp[0][0], linewidth=2, color='#FF0000')
        ax.set_ylim(PLOT_CONFIG_TEMP[0]['ylim'])
        ax.set_title(PLOT_CONFIG_TEMP[0]['title'], position=(0.5, 0.8), color='white')
        fig.canvas.draw()  # Draw the figure using the Agg backend
        image = Image.frombytes('RGB', fig.canvas.get_width_height(),
                                fig.canvas.tostring_rgb()).convert('RGB')
        draw1.rectangle((0, 0, 280, 240), fill=(0, 0, 0))
        buffer1.paste(image)
        disp.image(buffer1)

try:
    print("Looping")
    while True:
        update_data_load()
        update_data_temp()
        #update_data_disk()
        update_plot()
        time.sleep(REFRESH_RATE)
except KeyboardInterrupt:
    print("Loop interrupted by user.")
finally:
    pin7.close()
    print("Exiting program.")
