#!/usr/bin/python

import os, sys

pname = ""
if len(sys.argv) < 2: sys.exit(0)
else: pname = sys.argv[1]
o = os.popen("ps axf | grep " + pname + " | grep -v grep | awk '{print \"kill -9 \" $1}' | exec $0").read()
o = o.replace(" ", "").replace("\n", "")
if not o: print("Ok!")
else: print(o)
