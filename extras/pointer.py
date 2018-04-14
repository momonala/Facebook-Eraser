import pyautogui

old_loc = pyautogui.position()

while True:
    curr_loc = pyautogui.position()
    if curr_loc != old_loc:
        old_loc = curr_loc
        print(old_loc)
