# SuSentry
Linux Facial Recognition for using Su/Sudo, written in Python 3 using dlib and OpenCV 3

# Requirements
- Python 3+
- dlib with Python 3 bindings
- OpenCV
- Numpy
- YAML

##### Installing dlib: 
```
pip3 install dlib
```

##### Installing OpenCV
```
pip3 install opencv-contrib-python
```
##### YAML, Numpy
```
pip3 install pyyaml
pip3 install numpy
```

##### Folder Structure
```
|-susentry(dir)      
| |_images
| |_unknownimages
|_susentry.py
|_config.yml
|_dlib_face_recognition_resnet_model_v1.dat
|_shape_predictor_5_face_landmarks.dat
|_LICENSE
```

### Editing the Config File

The config file is in YAML and comes without any of the values filled in.
You can set Verbose to True or False (No quotes, only the folder paths are strings) 
If Verbose is True you can see the facial recognition in action, if set to False, everything happens quietly in the background.
Change the working directory to where you store the files. Example: "/home/user/susentry" (Include the quotations)
The rest of the values are the paths to the files included in the repository.

### First run

Run susentry.py once without any arguments: 
```
python3 susentry.py
```

It will take an image of your face and save it to the 'known' images folder. This is the picture the sudoers face will be compared against. 
You can add as many pictures as you want - all images in the known images folder will be iterated through until either
1) A match is found
or
2) All images have been checked and no match is found (in which case the login will fall back to the password method, and the picture of the failed facial recognition will be saved in the unknown images folder)

This means that you can choose to have more than one person access the same computer using facial recognition.
It is important that you do this step before proceeding below.

### Editing /etc/pam.d/common-auth 

We will be using Linux-PAM (Pluggable Authentication Modules) to call our script when a user uses su/sudo (To be more specific, anytime a password is required).
For those unfamiliar with PAM, you can learn more about PAM here:
http://www.linux-pam.org/Linux-PAM-html/

#### *** WARNING *** The file we are going to be editing is /etc/pam.d/common-auth 
##### Modifying these files is not to be taken lightly and if you do something incorrectly you may have to log in to single user mode and gain root priveleges to revert the common-auth file back.
Lets get started!

First, we want to place a bash script in our /usr/local/bin/ folder. This script is named 'susentry' and is located in this repository.
Find this line:
```
python3 /path/to/susentry.py -l
```
And change `/path/to/susentry.py` to the full path of your susentry.py python file.
Then, place this file in /usr/local/bin folder.

```
sudo cp susentry /usr/local/bin/susentry
```

We will need to make this file an executable.

```
sudo chmod +x /usr/local/bin/susentry
```

Next, we modify the PAM common-auth file:

```
sudo -i gedit /etc/pam.d/common-auth
```

Find this line in your common-auth file:

```
auth [success=1 default=ignore]     pam_unix.so nullok_secure
```

This line calls the module that asks the user for a password. If the module returns success (password correct), it skips the next line (success=1 means skip one line). 
So, if you want to use su/sudo, but instead of entering your password you use facial comparison, put this above the line above:

```
auth [success=2 default=ignore]     pam_exec.so debug log=/path/to/pamlogs.txt /usr/local/bin/susentry
```

Make sure you change `/path/to/pamlogs.txt` to where you want the PAM output to be saved. (This ouput is error output and stdin output from susentry and susentry.py - if you set Verbose to True that printed information will show up here)

Here is an example of a common-auth file with these changes on Ubuntu 20.04.1 LTS
```
#
# /etc/pam.d/common-auth - authentication settings common to all services
#
# This file is included from other service-specific PAM config files,
# and should contain a list of the authentication modules that define
# the central authentication scheme for use on the system
# (e.g., /etc/shadow, LDAP, Kerberos, etc.).  The default is to use the
# traditional Unix authentication mechanisms.
#
# As of pam 1.0.1-6, this file is managed by pam-auth-update by default.
# To take advantage of this, it is recommended that you configure any
# local modules either before or after the default block, and use
# pam-auth-update to manage selection of other modules.  See
# pam-auth-update(8) for details.

# here are the per-package modules (the "Primary" block)
auth [success=2 default=ignore]     pam_exec.so debug log=/home/user/susentry/pamlogs.txt /usr/local/bin/susentry
auth	[success=1 default=ignore]	pam_unix.so nullok_secure
# here's the fallback if no module succeeds
auth	requisite			pam_deny.so
# prime the stack with a positive return value if there isn't one already;
# this avoids us returning an error just because nothing sets a success code
# since the modules above will each just jump around
auth	required			pam_permit.so
# and here are more per-package modules (the "Additional" block)
auth	optional			pam_cap.so 
# end of pam-auth-update config
```

## Try it out!

Open a new terminal and type:
`sudo test`



## Please note:
### - Bright lights in the background, or blurry images will usually fail facial comparison.
### - By no means is this more secure than your password. If someone held up a clear enough picture of you, it would pass the facial recognition. 

