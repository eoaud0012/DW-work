import pyautogui
import pyperclip
import time

print(pyautogui.position())

count = 0
while(count < 10000):
    pyautogui.moveTo(917, 720)
    time.sleep(0.1)
    pyautogui.mouseDown(button='right')
    time.sleep(0.1)
    pyautogui.mouseUp(button='right')
    time.sleep(0.1)
    pyautogui.moveTo(985, 769)
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.press('enter')
    count += 1
    pyautogui.moveTo(1061, 720)
    time.sleep(0.1)
    