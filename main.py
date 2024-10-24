import random
import sys
import time
import cv2
from math import pow, sqrt
from mss import mss
import numpy as np

from win32 import win32api
import win32con
import pyautogui
import lib.viz as viz
from timer import Timer
# from python_imagesearch.imagesearch import *

if __debug__:
    cv2.namedWindow('res', cv2.WINDOW_NORMAL)

# The size of the window to scan for targets in, in pixels
# i.e. SQUARE_SIZE of 600 => 600 x 600px
SQUARE_SIZE = 1400
viz.SQUARE_SIZE = SQUARE_SIZE

# The maximum possible pixel distance that a character's center
# can be before locking onto them
TARGET_SIZE = 100
MAX_TARGET_DISTANCE = sqrt(2 * pow(TARGET_SIZE, 2))
viz.TARGET_SIZE = TARGET_SIZE
viz.MAX_TARGET_DISTANCE = MAX_TARGET_DISTANCE

# Create an instance of mss to capture the selected window square
sct = mss()

# Use the first monitor, change to desired monitor number
dimensions = sct.monitors[1]

# Compute the center square of the screen to parse
# dimensions['left'] = int((dimensions['width'] / 2) - (SQUARE_SIZE / 2))
# dimensions['top'] = int((dimensions['height'] / 2) - (SQUARE_SIZE / 2))
dimensions['left'] = 0
dimensions['top'] = 0
dimensions['width'] = 710
dimensions['height'] = SQUARE_SIZE

print(dimensions, flush=True)

# Calls the Windows API to simulate mouse movement events that are sent to OW
def mouse_move(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)

def mouse_click(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

# Determines if the Caps Lock key is pressed in or not
def is_activated():
    return win32api.GetAsyncKeyState(0x14) != 0


# def r(num, rand):
#     return num + rand * random.random()

def click_image(image, pos, action, timestamp, offset=5):
    pyautogui.FAILSAFE = False
    img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    if img is None:
        raise FileNotFoundError('Image file not found: {}'.format(image))
    height, width = img.shape
    point_height = dimensions['top'] + pos[1]
    point_width = dimensions['left'] + pos[0]
    
    # mouse_move(1,100)
    pyautogui.moveTo(point_width,point_height, timestamp)
    # time.sleep(random())
    pyautogui.leftClick()
    # mouse_click(point_width,point_height)
    # mouse_click(1,100)
    print(f'point_height: {point_height}, point_width: {point_width}', flush=True)
    return True

# Main lifecycle


# 预约天猫茅台
# steps = [
#     {
#         "image" : 'tmall_images/open_taobao.png',
#         "desc" : "打开淘宝",
#         "post_action": "click_random",
#         "timeout": 5
#     },
#     {
#         "image" : 'tmall_images/my_taobao.png',
#         "desc" : "进入我的淘宝",
#         "post_action": "click_random",
#         "timeout": 5
#     },
#     {
#         "image" : 'tmall_images/my_favorites.png',
#         "desc" : "进入我的收藏",
#         "post_action": "click_random",
#         "timeout": 5
#     },
#     {
#         "image" : 'tmall_images/select_maotai.png',
#         "desc" : "选择茅台",
#         "post_action": "click_random",
#         "timeout": 5
#     },
#     {
#         "image" : 'tmall_images/yuyue_maotai.png',
#         "desc" : "预约茅台",
#         "post_action": "click_random",
#         "timeout": 5
#     },
#     {
#         "image" : 'tmall_images/yuyue_chenggong.png',
#         "desc" : "预约成功",
#         "post_action": "click_random",
#         "timeout": 5
#     },
#     {
#         "image" : 'tmall_images/taobao_tab.png',
#         "desc" : "淘宝标签页",
#         "post_action": "click_random",
#         "timeout": 5
#     },
#     {
#         "image" : 'tmall_images/close_taobao.png',
#         "desc" : "关闭淘宝",
#         "post_action": "click_random",
#         "timeout": 2.5
#     },
# ]
steps = [
    {
        "image" : 'tmall_images/maotai_shoppingcar.png',
        "desc" : "进入茅台购物车",
        "post_action": "click_random",
        "timeout": 5
    },
    {
        "image" : 'tmall_images/select_all_shoppingcar.png',
        "desc" : "勾选购物车",
        "post_action": "click_random",
        "timeout": 5
    },
    {
        "image" : 'tmall_images/jiesuan_shoppingcat.png',
        "desc" : "结算购物车",
        "post_action": "wait_click_center",
        "timeout": 5
    },
    {
        "image" : 'tmall_images/select_alipay.png',
        "desc" : "勾选支付宝支付",
        "post_action": "click_random",
        "timeout": 5
    },
    {
        "image" : 'tmall_images/tijiaodingdan.png',
        "desc" : "提交订单",
        "post_action": "click_random",
        "timeout": 5
    },
]
def start_tmall():
    timers = Timer()
    timers.start()

def check_switch(old_screen):
    while True: 
        frame = np.asarray(sct.grab(dimensions))
        if viz.check_switch_screen(old_screen=old_screen, new_screen=frame, precision=0.2):
            return True
        time.sleep(0.3)

def search_image(image):
    time_start = time.process_time()
    while True: 
        frame = np.asarray(sct.grab(dimensions))
        screen, top_left, bottom_right, center_point = viz.search_image(
            image=image, screen=frame)
        
        if __debug__:
            cv2.imshow('res', screen)

        if (time.process_time() - time_start) < val["timeout"]:
            if center_point[0] > 1:
                print(f'搜索到目标图像，用时{str(time.process_time() - time_start) }s')
                return True, screen, center_point, (random.randint(top_left[0], bottom_right[0]), random.randint(top_left[1], bottom_right[1]))

        else:
            print("timeout")
            return False, screen, (-1, -1), (-1, -1)
    
        # Press `q` to stop the program
        if cv2.waitKey(25) & 0xFF == ord("q"):
                sys.exit(1)
        
        time.sleep(0.3)

for key, val in enumerate(steps):
    
    print(f'开始执行步骤: {key} , {val}', flush=True)

    search = cv2.imread( val["image"] )
    cv2.imshow('img', search)
    is_search, screen, center_point, random_point = search_image(val["image"])
    # # 查到图片后操作
    print(f'is_search: {is_search}', flush=True)
    # print(f'val.get("post_action"): {val.get("post_action")}', flush=True)
    print(f'len(val["post_action"]): {len(val["post_action"])}', flush=True)
    if is_search == True:
        if val.get("post_action"):
            if len(val["post_action"]) > 1:
                print(f'开始执行动作{val["post_action"]}', flush=True)
                # 休眠2s内任意数
                time.sleep(random.random() * 2)
                if val["post_action"] == 'click_center':
                    is_move = click_image(screen, center_point, "left", 0.2, offset=5)
                if val["post_action"] == 'click_random':
                    is_move = click_image(screen, random_point, "left", 0.2, offset=5)
                if val["post_action"] == 'wait_click_center':
                    start_tmall()
                    is_move = click_image(screen, random_point, "left", 0.2, offset=5)
                print('开始验证点击')
                check_switch(screen)
                print('验证通过')
    
    # 在超时时间内没有找到图片
    else:
        if val.get("timeout_action"):
            pass


sct.close()
cv2.destroyAllWindows()