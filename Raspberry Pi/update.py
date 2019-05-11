#!/usr/bin/env python

import os
import subprocess
import time
import stat
def disk_exists(path):
     try:
             return stat.S_ISBLK(os.stat(path).st_mode)
     except:
             return False

basedir = '/dev/disk/by-path/'

def search():
    print("searching", time.time())
    disks = []
    for d in os.listdir(basedir):
        #Only show usb disks and not partitions
        if 'usb' in d:# and 'part' not in d:
            path = os.path.join(basedir, d)
            link = os.readlink(path)
            disks.append('/dev/' + os.path.basename(link))

    d = {}
    lin=[]

    for disk in disks:
        diskkey = "'" + disk + "'"
        process = ['df | grep ' + disk]
        grep = subprocess.Popen(process, shell=True, stdout=subprocess.PIPE)
        line = grep.stdout.read().decode()
        for lines in line.split("\n"):
            if str(lines) != "":
                lin.append(lines)
    lin2=[]

    for li in lin:
        if li =="":
            del(li)
        if li in lin2:
            pass
        else:
            lin2.append(li)

    for x in lin2:
        mount = x.split(" ")[0]
        folder = x.split("% ")[1]
        files = os.listdir(folder)
        if "TOOXO_UPDATE" in files:
            pass
        else:
            print("no")
            continue
        print("im in")
        for file in files:
            sub = ["cp", folder+"/"+file, "/home/pi/"+file]
            subprocess.call(sub)
        os.system('sudo shutdown -r now')
