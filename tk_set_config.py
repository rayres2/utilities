#!/usr/bin/env python

'''
DESCRIPTION
Utility to automate copying and renaming hosted-config packages from local vnc4
repo' to /etc/vnc/.  
Checks installed pkg by comparing file shasum.
For Linux and MacOS.

USAGE
* Clone vnc4 repo
* Run as sudo
* If app fails to find your vnc4 repo, set vnc4_path below 

TO DO
* Move UI to Tkinter/Tk
* Add Windows support
'''

from Tkinter import Tk, Label, Button, Entry, IntVar, END, N, S, E, W
import shutil
#import curses
import platform
import hashlib
import os
import re
#import time


app_version = '1.1'

# home = os.getenv('HOME')
home = '/Users/ra2/'
vnc4_path = r'/Users/ra2/Source/vnc4/libs/hosted/resources/'
vnc4_path_regex = r'vnc4.libs.hosted.resources'

# If app doesn't locate the path to vnc4, set manually:
# vnc4_path = r''
vnc4_live_cfg = 'HostedConfig-Live.pkg'
vnc4_int_cfg = 'HostedConfig-Integration.pkg'
product_cfg = 'CloudConfig.pkg'
current_config = 'foo'

# Assumes VNC Server/Viewer has already been installed
nix_product_path = r'/etc/vnc/'
win_product_path = r''
product_path = nix_product_path


def get_vnc4_path():
    path = None
    for root, dirs, files in os.walk(home, topdown=True):
        for name in root:
            if re.search(vnc4_path_regex, root):
                path = root
                return path
    if not path:
        raise Exception("Can't find vnc4 repo under " + home)

def get_hash(file):
    #Generate the hash for each file
    sha256 = hashlib.sha256()
    f = open(file, 'rb')
    try:
        sha256.update(f.read())
    finally:
        f.close()
        return sha256.hexdigest()

# Returns shasums for HostedConfig packages in local vnc4 repo
def get_reference_shasums():
    hosted_config_shasums = [
                            get_hash(os.path.join(vnc4_path, vnc4_int_cfg)),
                            get_hash(os.path.join(vnc4_path, vnc4_live_cfg))]
    return hosted_config_shasums

''' Compares shasum of installed CloudConfig.pkg to the live/production config
in local vnc4 repo '''
def is_live_config(reference_shasums):
    shasum_cloudconfig = get_hash(product_path + product_cfg)
    # Integration is at index 0, Live at index 1
    if shasum_cloudconfig == reference_shasums[1]:
        return True
    else:
        return False

# Copy and rename configs
def file_ops(env):
        dest = product_path + product_cfg
        if env == 'live':
            src = os.path.join(vnc4_path, vnc4_live_cfg)
        elif env == 'int':
            src = os.path.join(vnc4_path, vnc4_int_cfg)
        try:
            shutil.copyfile(src, dest)
        # eg. src and dest are the same file
        except shutil.Error as e:
            print('Error: %s' % e)
        # eg. source or destination doesn't exist
        except IOError as e:
            print('Error: %s' % e.strerror)

# On start-up, check for existing CloudConfig.pkg
def is_config_present(reference_shasums):
    if not os.path.isfile(product_path + product_cfg):
        status = 'None'
    else:
        if is_live_config(reference_shasums):
            status = 'LIVE'
        else:
            status = 'INTEGRATION'
    return status


def main(): 
    root = Tk()
    my_gui = root
    
    reference_shasums = get_reference_shasums()

    root.title("CloudConfig Switcher")

    current_config.set('foobar')

    # UI elements
    label_version = Label(root, text=app_version)
    label_current_config = Label(root, textvariable=current_config)
    live_button = Button(root, text="Live", command=lambda: file_ops('live'))
    int_button = Button(root, text="Integration", command=lambda: file_ops('int'))
    quit_button = Button(root, text="Quit", command=lambda: quit())

    # LAYOUT
    label_current_config.grid(row=0, column=0, columnspan=3, sticky=(W))
    live_button.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=(N, S, E, W))
    int_button.grid(row=2, column=1, rowspan=1, columnspan=1, sticky=(N, S, E, W))
    label_version.grid(row=3, column=2, columnspan=1, sticky=E)
    quit_button.grid(row=3, column=0, sticky=W+E)

    col_count, row_count = root.grid_size()

    for col in xrange(col_count):
        root.grid_columnconfigure(col, minsize=60)

    for row in xrange(row_count):
        root.grid_rowconfigure(row, minsize=40)

    root.mainloop()


if __name__ == '__main__': 
    main()
