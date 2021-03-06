#!/usr/bin/python

import datetime, os, argparse, time, getpass, sys

start_hour = 19
start_minute = 1
end_hour = 7
end_minute = 0
timeout = 1
high_temp = 6500
low_temp = 4000

red_mode = False
dbg = False

def shift_to_red():
    global red_mode
    red_mode = True
    if dbg: print("Shiffting into RED mode")
    os.popen("/usr/bin/redshift -O " + str(low_temp))

def shift_to_blue():
    global red_mode
    red_mode = False
    if dbg: print("Shiffting into BLUE mode")
    os.popen("/usr/bin/redshift -O " + str(high_temp))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage="python " + __file__ + " --htemp=6500 --ltemp=4000 --timeout=1 --start=19:00 --end=07:00 &")
    parser.add_argument("--start", help="Starting time (19:30 e.g.)")
    parser.add_argument("--end", help="Finishing time (07:00 e.g.)")
    parser.add_argument("--timeout", help="Timeout in seconds (1 by default)")
    parser.add_argument("--htemp", help="High temperature (6500 by default)")
    parser.add_argument("--ltemp", help="Low temperature (4000 by default)")
    args = parser.parse_args()

    if getpass.getuser() != "root":
        print("Script must be run by root user.")
        sys.exit()

    if args.start:
        start_hour = int(args.start.split(":")[0])
        start_minute = int(args.start.split(":")[1])

    if args.end:
        end_hour = int(args.end.split(":")[0])
        end_minute = int(args.end.split(":")[1])
    
    if args.timeout:
        timeout = int(args.timeout)

    if args.htemp:
        htemp = int(args.htemp)

    if args.ltemp:
        ltemp = int(args.htemp)

    now = datetime.datetime.now()
    
    wait_flag = True
    red_mode = False
    
    #end_hour = 0
    #end_minute = 28
    
    while True:
        now = datetime.datetime.now()
        if end_hour < start_hour:
            if now.hour >= start_hour and now.minute >= start_minute and not red_mode:
                shift_to_red()
            if wait_flag and now.hour >= 0 and now.minute >= 0 and now.hour * 60 + now.minute < end_hour * 60 + end_minute:
                wait_flag = False
                if not red_mode:
                    shift_to_red()
            if not wait_flag and now.hour >= end_hour and now.minute >= end_minute and red_mode:
                shift_to_blue()
                wait_flag = True
        else:
            if now.hour == start_hour:
                if now.minute >= start_minute and not red_mode:
                    shift_to_red()
            elif now.hour > start_hour and now.hour < end_hour and not red_mode:
                shift_to_red()
            elif now.hour >= end_hour and now.minute >= end_minute and red_mode:
                shift_to_blue()
        time.sleep(timeout)
