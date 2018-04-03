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

import shutil
import curses
import platform
import hashlib
import os
import re

app_version = '1.1'

home = os.getenv('HOME')
# home = ''

vnc4_path = None
vnc4_path_regex = r'vnc4.libs.hosted.resources'

# If app doesn't locate the path vnc4 defined by vnc4_path_regex, set manually:
# vnc4_path = r'<path>'

vnc4_live_cfg = 'HostedConfig-Live.pkg'
vnc4_int_cfg = 'HostedConfig-Integration.pkg'
product_cfg = 'CloudConfig.pkg'

# Assumes VNC Server/Viewer has already been installed
product_path = r'/etc/vnc/'


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
def get_reference_shasums(vnc4_path):
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
def file_ops(env, vnc4_path):
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

# Main menu actions
def set_config(stdscr, user_input, reference_shasums, vnc4_path):
    if user_input == ord('1'):
        file_ops('live', vnc4_path)
        if is_live_config(reference_shasums):
            stdscr.addstr(10, 2, "- LIVE cfg copied to " + product_path)
            stdscr.addstr(11, 2, "- Press any key > ")
            stdscr.refresh()
            stdscr.getch()
    elif user_input == ord('2'):
        file_ops('int', vnc4_path)
        if not is_live_config(reference_shasums):
            stdscr.addstr(10, 2, "- INTEGRATION cfg copied to " + product_path)
            stdscr.addstr(11, 2, "- Press any key > ")
            stdscr.refresh()
            stdscr.getch()
    elif user_input == ord('q'):
        return quit

def app_header(stdscr, initial_status, platform_os):
    stdscr.addstr(1, 2, "v" + app_version)
    stdscr.addstr(2, 2, "*************************************")
    stdscr.addstr(3, 2, "*")
    stdscr.addstr(3, 4, "      CLOUD CONFIG SWITCHER      ", curses.A_BOLD)
    stdscr.addstr(3, 38, "*")
    stdscr.addstr(4, 2, "*")
    stdscr.addstr(4, 38, "*")
    stdscr.addstr(5, 2, "*")
    stdscr.addstr(5, 10, "Config:")
    stdscr.addstr(5, 18, initial_status, curses.A_STANDOUT)
    stdscr.addstr(5, 38, "*")
    stdscr.addstr(6, 2, "*************************************")
    stdscr.addstr(7, 2, "(Platform: " + platform_os + ')')
    stdscr.addstr(9, 2, "[1]:LIVE, [2]:INTEGRATION, [q]:exit > ")


def main(stdscr, vnc4_path):
    platform_os = platform.system()   
    if vnc4_path == None:
        stdscr.addstr(1, 2, 'Searching %s for vnc4 repo...' % home)
        stdscr.refresh()
        vnc4_path = get_vnc4_path()
    reference_shasums = get_reference_shasums(vnc4_path)
    while True:
        try:
            # Determine current config, if any
            initial_status = is_config_present(reference_shasums)
            stdscr.clear()
            # Display app header
            app_header(stdscr, initial_status, platform_os)
            stdscr.refresh()
            user_input = stdscr.getch()
            choice = set_config(stdscr, user_input, reference_shasums, vnc4_path)
            if choice == quit:
                break
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    curses.wrapper(main, vnc4_path)
