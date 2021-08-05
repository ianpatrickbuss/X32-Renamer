import cv2 
import numpy as np
import pyautogui as pag
from os import remove
from sys import argv
import time
def init():
    pag.hotkey('winleft','5')
    pag.hotkey('winleft','f')
    pag.PAUSE = 0.2
    pag.click(x=60,y=760)
    pag.click(x=10,y=420)

def clear_input_names():
    points = get_matches('channel.png')
    for x,y in points:
        new_y = y-14
        name_channel((x,new_y),' ')
    points = shift_screen_reset_points(points[-3:])[-7:]
    for x,y in points:
        new_y = y-14
        name_channel((x,new_y),' ')
    # Monitors
    pag.click(x=60,y=760)
    x,y = get_matches('bus_sends.png')[0]
    pag.click(x=x+5,y=y+5)
    points = get_matches('channel.png')
    for x,y in points:
        new_y = y-14
        name_channel((x,new_y),' ')
    pag.click(x=60,y=760)
    pag.click(x=10,y=420)

def get_ioplot():
    with open('io.plot','r') as f:
        blob = f.read()
        channels = blob.split('\n')
    return channels[:-1]

def name_channel(pos,name):
    x, y = pos
    pag.click(x=x+15,y=y-14,button='right')
    pag.write(name)
    pag.press('enter')

def name_channels():
    # Init
    """
        Need to get the number of channels and name each channel in the io.plot
        Determine:
            1. Are there more channels that need to be named vs namable channels on screen
            2. Are there monitors that need to be named
        
    """
    channels = get_ioplot()
    points = get_matches('channel.png')
    i = 0
    for channel in channels:
        if i == len(points):
            points = shift_screen_reset_points(points[-3:])
            i = 0
        if channel == '--':
            pag.click(x=60,y=760)
            x,y = get_matches('bus_sends.png')[0]
            pag.click(x=x+5,y=y+5)
            points = get_matches('channel.png')
            
            i = 0
            continue
        pos = points[i]
        name_channel(pos,channel)
        i += 1

def shift_screen_reset_points(comp_points):
    old_points = [x[0] for x in comp_points]
    old_points = (old_points[0],old_points[-1])
    width = (old_points[1]-old_points[0])+40
    pag.click(x=10,y=20)
    pag.screenshot('named_inputs.png',region=(old_points[0],comp_points[0][1]-38,width,100))
    # Click Scrollbar
    pag.click(x=old_points[-1],y=760)
    named_inputs_pos = get_matches('named_inputs.png')
    remove('named_inputs.png')
    start_point = named_inputs_pos[0][0]+width
    points = get_matches('channel.png')

    final_points = []
    for point in points:
        if point[0]>start_point:
            final_points.append(point)
    return final_points[2:]

def get_matches(image_path: str) -> list:
    pag.screenshot('x32.png')
    img_rgb = cv2.imread('x32.png')
    template = cv2.imread(image_path)
    w, h = template.shape[:-1]
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .9
    loc = np.where(res >= threshold)
    points = []
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        x, y = pt
        points.append(pt)
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    # Debugging:
    # cv2.imwrite('result.png', img_rgb)
    if len(points)>1:
        points = points[:-1]

    remove('x32.png')
    return points

tic = time.perf_counter()
init()
if "".join(argv[1:]) == 'clear':
    clear_input_names()
else:
    name_channels()
toc = time.perf_counter()
print(f"This took {toc - tic:0.4f} seconds")
