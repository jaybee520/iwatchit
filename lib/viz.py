import cv2
from math import pow, sqrt
import numpy as np

# The size of the window to scan for targets in, in pixels
# i.e. SQUARE_SIZE of 600 => 600 x 600px
SQUARE_SIZE = 600

# The maximum possible pixel distance that a character's center
# can be before locking onto them
TARGET_SIZE = 100
MAX_TARGET_DISTANCE = sqrt(2 * pow(TARGET_SIZE, 2))

# Dark Magenta
H_LOW = 139
S_LOW = 96
V_LOW = 129

# Light Magenta
H_HIGH = 169
S_HIGH = 225
V_HIGH = 225

magenta_dark = np.array([H_LOW, S_LOW, V_LOW])
magenta_light = np.array([H_HIGH, S_HIGH, V_HIGH])


def process(frame):
    import time
    time.sleep(1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # cv2.imshow('res', hsv)
    magenta_color_range = cv2.inRange(hsv, magenta_dark, magenta_light)

    

    res = cv2.bitwise_or(frame, frame, mask=magenta_color_range)
    res = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY)
    cv2.imshow('res', res)
    # Extract magenta colors
    thresh = cv2.adaptiveThreshold(res, 1, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 15, 1)

    # Locate the objects with magenta outline
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Create a convex hull polygon around each extracted object
    contours = map(lambda ct: cv2.convexHull(ct, False), contours)

    # Sort the objects and extract the biggest
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if __debug__:
        # Yellow contours are all contour matches, before filtering out
        cv2.drawContours(frame, contours, -1, (255, 255, 0), 1)

    # Attempt to filter out extraneous contours, so that only characters exist
    return list(filter(contour_filter, contours))

def check_switch_screen(old_screen, new_screen, precision=0.2):
    old_screen_gray = cv2.cvtColor(old_screen, cv2.COLOR_BGR2GRAY)
    new_screen_gray = cv2.cvtColor(new_screen, cv2.COLOR_RGB2GRAY)
    res = cv2.matchTemplate(new_screen_gray, old_screen_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(min_val, flush=True)
    if min_val < precision:
        return True
    else:
        return False

def search_image(image, screen, precision=0.8):
    # import time
    # time.sleep(1)

    img_rgb = cv2.imread(image)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
    if template is None:
        raise FileNotFoundError('Image file not found: {}'.format(image))
    template.shape[::-1]
    w,h = img_gray.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc
    # print(max_val, flush=True)
    if max_val < precision:
        return screen, [-1, -1], [-1, -1], [-1, -1]
    
    bottom_right = (max_loc[0] + w, max_loc[1] + h )
    helf_w = (bottom_right[0] - top_left[0]) / 2
    helf_h = (bottom_right[1] - top_left[1]) / 2
    point_w = int(helf_w + top_left[0])
    point_h = int(helf_h + top_left[1])
    # print(drow_w , drow_h , helf_w, helf_h ,point_w, point_h, flush=True)
    center_left = (point_w - 1, point_h - 1)
    center_right = (point_w + 1, point_h + 1)
    print(f'center_w: {point_w}, center_h: {point_h}',flush=True)
    cv2.rectangle(screen, center_right, center_left, (0, 0, 255), 2)
    cv2.rectangle(screen, top_left, bottom_right, (0, 0, 255), 2)
    return screen, top_left, bottom_right, (point_w, point_h)

def contour_distance(ct):
    moment = cv2.moments(ct)
    if moment["m00"] == 0:
        return -1, None

    cx = int(moment["m10"] / moment["m00"])
    cy = int(moment["m01"] / moment["m00"])

    mid = SQUARE_SIZE / 2
    x = (mid - cx) if cx < mid else cx - mid
    y = (mid - cy) if cy < mid else cy - mid
    return [x, y]


def contour_filter(ct):
    x, y = contour_distance(ct)
    
    # Ensure that that the target is within the user defined max range
    if x == -1 or x > TARGET_SIZE or y > TARGET_SIZE:
        return False

    # Attempt to filter out small contours
    if cv2.contourArea(ct) < 1000:
        return False

    # Calculate the width and height of the contour
    extreme_left = tuple(ct[ct[:, :, 0].argmin()][0])
    extreme_right = tuple(ct[ct[:, :, 0].argmax()][0])
    extreme_top = tuple(ct[ct[:, :, 1].argmin()][0])
    extreme_bottom = tuple(ct[ct[:, :, 1].argmax()][0])
    width = extreme_right[0] - extreme_left[0]
    height = extreme_bottom[1] - extreme_top[1]

    if width == 0 or height == 0:
        return False

    # Attempt to filter out wide objects
    if abs(width / height) > 2.5:
        return False

    return True