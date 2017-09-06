#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Requirements: colorama
$> pip install colorama
"""

import os, sys, time, random, threading, argparse
from colorama import Fore

py_ver = sys.version_info.major
if py_ver == 2:
    reload(sys)
    sys.setdefaultencoding('utf8')

timeout = 1
last_index = 1024 #2^10
wprob = 5
rows = []
seed = []
finished = False
words = ["fuzz", "n0p", "hex", "byte", "hack", "explo0it", "0day", "vuln"]
colors = {
    'black' : Fore.BLACK,
    'blue' : Fore.BLUE,
    'green' : Fore.GREEN,
    'red' : Fore.RED,
    'white' : Fore.WHITE,
    'yellow' : Fore.YELLOW
}
color = Fore.RED
words_bytes = {}

#psuedo random arguments
a = random.randint(10**6, 10**10)
c = random.randint(10**6, 10**10)
m = random.randint(10**6, 10**10)
last_random = random.randint(10**9, 10**12)

def get_pseudo_random(from_num = 0, to_num = 0):
    global last_random, a, c, m
    last_random  = (a * last_random + c) % m
    if to_num > 0 and to_num >= from_num:
        last_random = from_num + last_random % to_num
    if from_num > 0 and last_random < from_num:
        last_random += from_num
    if last_random < sys.maxint:
        last_random = int(last_random)
    return last_random

def get_boxed_string(s):
    padding = 5
    slen = padding * 2 + len(s) - 2
    s = u'║' + ('{:^' + str(slen) + '}').format(s) + u'║'
    up = u'╔' + "═" * slen + u'╗\n'
    down = u'╚' + "═" * slen + u'╝\n'
    s = up + s + "\n" + down
    return s

def get_ascii_boxed_string(s):
    padding = 5
    slen = padding * 2 + len(s) - 4
    s = " |" + ('{:^' + str(slen) + '}').format(s) + "| "
    up = " #" + "~" * slen + "# \n"
    down = " #" + "~" * slen + "# \n"
    s = up + s + "\n" + down
    return s

def get_word_bytes(w):
    res = ""
    delimeter = " "
    for c in w:
        res += ("%X" % ord(c)) + delimeter
    res = res[:-1] #remove last delimeter character
    return res

def insert_into_center(s1, s2):
    #inserting s1 in the middle of s2
    if s1[0] == "\n": s1 = s1[1:]
    if s1[-1] == "\n": s1 = s1[:-1]
    old_s2 = s2
    s2 = s2.split("\n")
    h2 = len(s2)
    w2 = len(s2[0])

    s1 = s1.split("\n")
    h1 = len(s1)
    w1 = len(s1[0])

    y = int(h2 / 2) - int(h1 / 2)
    x = int(w2 / 2) - int(w1 / 2)

    if y < 0: y = 0
    if x < 0: x = 0
    
    try:
        for line in s1:
            s2[y] = s2[y][:x] + line + s2[y][(len(line) + x):]
            y += 1
    except BaseException as e:
        return old_s2

    return "\n".join(s2)

def fill_seed():
    global seed, rows_num
    if len(seed) < rows_num:
        seed = [get_new_row()] + seed

def start_filling():
    global timeout, finished
    while True:
        if finished: return
        fill_seed()
        time.sleep(timeout / 3)

def get_printable_string(s, delimeter=" "):
    s = s.split(delimeter)
    res = ""
    for byte in s:
        try:
            byte = int(byte, 16)
        except BaseException as e:
            byte = random.randint(0, 255)
        try:
            if byte >= 33 and byte <= 126: #ascii printable range
                byte = chr(byte)
            else:
                byte = "."
        except BaseException as e:
            byte = "."
        res += byte
    return res

def get_random_hex_byte():
    byte = "%X" % random.randint(0, 255)
    if len(byte) < 2: byte = "0" + byte
    return byte

def get_new_row():
    global last_index, pad1_len, pad2_len, col1_size, words, wprob
    index_str = ('{:0' + str(col1_size) + '}').format(last_index)
    last_index += 1

    delimeter = " "
    bytes_str = ""
    blen = int(col2_size / 3)
    
    #is random word must be inserted
    inserting = random.randint(1, 100) <= wprob #inserting random word with "wprob" % probability
    word = ""
    index = 0
    is_word_empty = True
    
    def gen_word(word):
        for c in word:
            yield c
    
    if inserting:
        is_word_empty = False
        word = random.choice(words)
        index = random.randint(1, blen - len(word) - 1)
        word = gen_word(word)
    
    for i in range(blen):
        if i >= index and inserting and not is_word_empty:
            ch = ""
            try:
                ch = next(word)
            except StopIteration as e:
                is_word_empty = True
                bytes_str += get_random_hex_byte() + delimeter
                continue
            if ch:
                ch = ("%X" % ord(ch))
                bytes_str += ch + delimeter
            else:
                bytes_str += get_random_hex_byte() + delimeter
        else:
            bytes_str += get_random_hex_byte() + delimeter
    bytes_str = bytes_str[:-1] #removing last space

    char_str = get_printable_string(bytes_str, delimeter)
    row = index_str + delimeter * pad1_len + bytes_str + delimeter * pad2_len + char_str
    return row

def init_rows():
    global rows, seed, rows_num
    for i in range(rows_num * 2):
        seed = [get_new_row()] + seed
    for i in range(rows_num):
        rows.append(seed.pop())

def iter_rows(rows):
    global seed
    rows = rows[1:]
    rows += [seed.pop()]
    return rows

def print_rows(rows, insert="", ascii_mode = False):
    global columns_num, words, words_bytes, color
    output = ""
    for row in rows:
        output += row + "\n"
    output = output[:-1] #remove last '\n' character
    output = ('{:^' + str(columns_num) + '}').format(output)
    if insert:
        if ascii_mode:
            output = insert_into_center(get_ascii_boxed_string(insert), output)
        else:
            output = insert_into_center(get_boxed_string(insert), output)
    #coloring some words
    for w in words:
        output = output.replace(w, color + w + Fore.RESET)
        output = output.replace(words_bytes[w], color + words_bytes[w] + Fore.RESET)
    print(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage= __file__ + " --speed=10 --message='Hello, world' --msg_time=3 --msg_timeout=5 --box_type=ascii --words=some,words --color=blue --words_prob=90")
    parser.add_argument("--width", help="Terminal width in characters count (auto set)")
    parser.add_argument("--height", help="Terminal heghti in rows count (auto set)")
    parser.add_argument("--speed", help="speed of running lines (in iterations per second). Default: 10")
    parser.add_argument("--message", help="Message text to show ('no' if message doesn't need to appear)")
    parser.add_argument("--msg_time", help="Time of showing message in seconds (5 by default)")
    parser.add_argument("--msg_timeout", help="Timeout of showing message in seconds (10 by dafault)")
    parser.add_argument("--box_type", help="Type of box in which message appears ('ascii' or 'unicode'). Default: 'unicode'")
    parser.add_argument("--words", help="Words to randomly insert into (separated by commas), 'no' if words doesn't need to insert.")
    parser.add_argument("--words_prob", help="Probability of showing one of words on each line (from 1 to 100, 5 by default).")
    parser.add_argument("--color", help="Color of words. Possible values: black, blue, green, red, white, yellow")
    args = parser.parse_args()
    
    try:
        rows_num, columns_num = os.popen('stty size', 'r').read().split()
        rows_num = int(rows_num)
        columns_num = int(columns_num)
    except BaseException as e:
        #test mode
        rows_num = 40
        columns_num = 140
    
    col1_size = 8
    pad1_len = 2
    pad2_len = 3
    col2_size = int((columns_num - col1_size - (pad1_len + pad2_len)) / 4) * 3 # 75% of width
    col3_size = int((columns_num - col1_size - (pad1_len + pad2_len)) / 4)     # 25% of width
    
    speed = 10
    timeout = 1.0 / speed
    box_type = "unicode"
    message = "0DAY HAS BEEN FOUND!"
    
    show_timeout = 10
    text_showing_time = 5 #must be greater than timeout
    last_showed_time = time.time()
    last_timeout_time = time.time()
    is_showing = False
    
    if args.speed:
        timeout = 1.0 / float(args.speed)
    
    if args.color:
        if args.color in colors.keys():
            color = colors[args.color]
    
    if args.words:
        if args.words == "no":
            words = []
        else:
            words = args.words.split(",")
    
    if args.box_type and args.box_type == "ascii":
        box_type = "ascii"
    
    if args.msg_timeout:
        show_timeout = float(args.msg_timeout)
    
    if args.msg_time:
        text_showing_time = float(args.msg_time)
    
    if args.message:
        message = args.message
    
    if args.words_prob:
        wprob = int(args.words_prob) % 100
    
    for w in words:
        words_bytes[w] = get_word_bytes(w)
    
    init_rows()
    threading.Thread(target=start_filling).start()    

    while True:
        try:
            rows = iter_rows(rows)
            if time.time() - last_showed_time >= show_timeout and not is_showing:
                is_showing = True
                last_timeout_time = time.time()
            if is_showing and time.time() - last_timeout_time >= text_showing_time:
                is_showing = False
                last_showed_time = time.time()
            if is_showing:
                if box_type == "ascii":
                    print_rows(rows, message, True)
                else:
                    print_rows(rows, message)
            else:
                if box_type == "ascii":
                    print_rows(rows=rows, ascii_mode=True)
                else:
                    print_rows(rows)
            time.sleep(timeout)
        except KeyboardInterrupt as e:
            finished = True
            break
    sys.exit()
