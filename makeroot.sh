#!/bin/bash

# To call this script: sudo readonly.sh /path/to/susentry/dir/

# First, make the owner of the entire susentry directory root.
# the -R flag makes it so it will recursively set every file and folder in this
# directory as root.
sudo chown -R root:root $1

# Then, give root executable permissions
sudo chmod -R 700 $1

# Exit successfully
exit 0

