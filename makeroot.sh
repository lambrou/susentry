#!/bin/bash

# To call this script: sudo ./makeroot.sh /path/to/susentry/dir/

# Makes the owner of the file/directory root.
# the -R flag makes it so it will recursively set every 
# file and folder in a directory as root.
sudo chown -R root:root $1

# Then, give root executable permissions
sudo chmod -R 700 $1

# Exit successfully
exit 0

