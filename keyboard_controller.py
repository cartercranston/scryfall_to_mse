import keyboard
import pyautogui
import os
import sys
import time
import threading

event = threading.Event()
def stop():
    print("escape was pressed")
    event.set()
    

def create_card_from_string(s, first_card = False):
    """Read a specially formatted text file, and type the correct output using the keyboard. Text files should have command keys (like control, arrow keys or enter) separated by two line breaks from text, or by four line breaks from other command keys"""
    # make new card
    if not first_card:
       keyboard.press_and_release('control+enter')

    if first_card:
        s = s[7:]
    
    # each file starts with text to be typed
    send=False
    
    for line in s.split("\n\n"):
        if not event.is_set():
            # lines which need to be sent as special characters are separated from text to be typed by two line breaks
            if send and line:
                if "make_image;" in line:
                    time.sleep(0.03)
                    pyautogui.doubleClick()
                    time.sleep(0.5)
                else:
                    time.sleep(0.01)
                    keyboard.send(line)
                    time.sleep(0.03)
                send = False
            else:
                # line may contain more than one "line" in the typical sense
                keyboard.write(line, delay=0.002)
                send = True
        else:
            sys.exit()

def connect_dir_to_keyboard(path):
    """Goes through a directory five files at a time whenever enter is pressed"""
    keyboard.add_hotkey('esc', stop)

    try:
        files = os.listdir(path)
    except FileNotFoundError:
        print("The directory has not yet been created")
        sys.exit(1)
    else:
        print("keyboard is ready: ensure that your mouse is in the correct position and MSE knows the location of your images folder, than press enter")

    keyboard.wait('enter')
    with open(os.path.join(path, files[0]), "rb") as f:
        s = f.read()
    create_card_from_string(s.decode("utf-8"), True)

    i = 0
    for file in files[1:]:
        if i % 20 == 0:
            keyboard.wait('enter')
        i += 1

        with open(os.path.join(path, file), "rb") as f:
            s = f.read()
        create_card_from_string(s.decode("utf-8"))