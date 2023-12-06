import keyboard
import os
import sys
import time

def create_card_from_string(s, first_card = False):
    """Read a specially formatted text file, and type the correct output using the keyboard. Text files should have command keys (like control, arrow keys or enter) separated by two line breaks from text, or by four line breaks from other command keys"""
    # make new card
    if not first_card:
       keyboard.press_and_release('control+enter')

    if first_card:
        s = s[7:]
        print(s)
    
    # each file starts with text to be typed
    send=False
    
    for line in s.split("\n\n"):
        # lines which need to be sent as special characters are separated from text to be typed by two line breaks
        if send and line:
            keyboard.send(line)
            time.sleep(0.05)
            send = False
        else:
            # line may contain more than one "line" in the typical sense
            keyboard.write(line, delay=0.001)
            send = True

def connect_dir_to_keyboard(path):
    """Goes through a directory five files at a time whenever enter is pressed"""
    keyboard.add_hotkey('esc', lambda: sys.exit(0))

    try:
        files = os.listdir(path)
    except FileNotFoundError:
        print("The directory has not yet been created")
        sys.exit(1)
    else:
        print("keyboard is ready: press enter")

    keyboard.wait('enter')
    with open(os.path.join(path, files[0])) as f:
        s = f.read()
    create_card_from_string(s, True)

    i = 0
    for file in files[1:]:
        if i % 5 == 0:
            keyboard.wait('enter')
        i += 1

        with open(os.path.join(path, file), "r") as f:
            s = f.read()
        create_card_from_string(s)