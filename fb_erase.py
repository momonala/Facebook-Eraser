from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import pyautogui
import cv2
import numpy as np
import keyboard
import sys


def click(where):
    '''click a specific location'''
    d = {
        'refresh': (500, 70),
        'likes': (100, 615),
        'comments': (100, 650),     
    }
    loc = d[where]
    pyautogui.moveTo(500, loc[1],  DURATION)
    pyautogui.moveTo(*loc,  DURATION)
    pyautogui.click()
    pyautogui.press('enter')
    pyautogui.moveTo(1030, 260,  DURATION)
    sleep(2)


# read in the login info
try:
    with open('login.txt', 'r') as f: 
        usrnm, pw, fb_name = [x.replace('\n', '').strip() for x in f.readlines()]
except FileNotFoundError:
    print('ERROR: login.txt file does not exist!')
    print('Create it with this format: \n\nemail\npassword\nfacebook username')
    sys.exit()

if len(sys.argv) == 1:
    print('ERROR Must specify "likes" or ""comments as command line arg')
    sys.exit()
post_type = sys.argv[1]
if post_type != 'likes' and post_type != 'comments':
    print('ERROR Must specify "likes" or "comments" as command line arg')
    sys.exit()

# some parameters
DURATION = 0.4  # time it takes to move cursor
SCREEN_RESOLUTION = (1024, 2000)
shift = 1020
comments_page = 'https://www.facebook.com/{}/allactivity?privacy_source=activity_log&log_filter=cluster_116'.format(fb_name)
likes_page = 'https://www.facebook.com/{}/allactivity?privacy_source=activity_log&log_filter=likes'.format(fb_name)

# template matching setup
icon = cv2.imread('icon.png', 0)
w, h = icon.shape[::-1]

# start the session
browser = webdriver.Firefox()
browser.get('https://www.facebook.com/')
browser.set_window_size(*SCREEN_RESOLUTION)
browser.set_window_position(0, 0)

# login
browser.find_element_by_id('email').send_keys(usrnm)
pass_box = browser.find_element_by_id('pass').send_keys(pw, Keys.ENTER)

# navigate to posts/likes page in a non-bot-like way
print("Telling Facebook we're not a bot ;)")
sleep(4)
if post_type == 'comments': browser.get(comments_page)
elif post_type == 'likes': browser.get(likes_page)
sleep(2)
pyautogui.press('esc')
click('refresh')
click(post_type)
click('refresh')

# DELETE SOME SHIT
deleting_enabled = False
print('STARTING -- deleting disabled')
print('press "d" to toggle deleting mode')
print('press "p" to pause')
print('press "q" to quit')
while True:
    if keyboard.is_pressed('q'):
        break
    if keyboard.is_pressed('p'):
        print('PAUSED. Press Enter to unpause.')
        input()
        print('UNPAUSED')
    if keyboard.is_pressed('d'):
        if deleting_enabled:
            deleting_enabled = False
            print('DELETING DISABLED')
        else:
            deleting_enabled = True
            print('DELETING ENABLED')

    # take a screeshot, --> grayscale, crop the search space
    img = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_BGR2GRAY)
    search_img = img[:, shift:(shift+60)]

    # Apply template matching, thresholding
    method = cv2.TM_CCOEFF_NORMED
    res = cv2.matchTemplate(search_img, icon, method)
    res[res < 0.9] = 0
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    loc = max_loc[0]+shift, max_loc[1]

    # if there are valid likes on the screen, click and delete, else scroll
    if np.sum(res) > 1 and max_loc[1] < 900:
        pyautogui.click(*loc)
        if deleting_enabled:
            pyautogui.moveRel(0, 60)
            pyautogui.click()
        sleep(1)
    else:
        pyautogui.scroll(-50)
