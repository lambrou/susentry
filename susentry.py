import sys
import os
import dlib
import glob
import cv2
import time
import numpy as np
import yaml

# Get script path
path = os.path.dirname(os.path.realpath(__file__))
config = path + "/config.yml"

# Load the YAML config file, config.yml
with open(config, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

verbose = cfg['verbose'] # Boolean value
predictor_path = cfg['predictor path']
face_rec_model_path = cfg['face recognition model path']
faces_folder_path = cfg['known faces folder path'] # Known (authorized) faces
ufaces_folder_path = cfg['unknown faces folder path'] # Unknown faces (no auth)

# Load all the models we need: a detector to find the faces, a shape predictor
# to find face landmarks so we can precisely localize the face, and finally the
# face recognition model.
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

# We need to take the dlib face vector and convert it to a numpy array
# so we may use numpy to perform maths operations on the face data
def dlibVect_to_numpyNDArray(vector):
    array = np.zeros(shape=128)
    for i in range(0, len(vector)):
        array[i] = vector[i]
    return array

# We subtract the unknown (unauthorized) face data array from the known array
# and then return the result. The result is known as the 'Euclidian Distance'
def get_euc_dist(known, unknown):
    npknown = dlibVect_to_numpyNDArray(known)
    npunknown = dlibVect_to_numpyNDArray(unknown)
    dist = np.linalg.norm(npknown - npunknown)
    return dist


def get_face_desc(image):
    img = dlib.load_rgb_image(image)
    if verbose:
        win = dlib.image_window()
        print("Processing file: {}".format(image))

        win.clear_overlay()
        win.set_image(img)

    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = detector(img, 1)
    if verbose: print("Number of faces detected: {}".format(len(dets)))

    # Now process each face we found.
    for k, d in enumerate(dets):
        if verbose: print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            k, d.left(), d.top(), d.right(), d.bottom()))
        # Get the landmarks/parts for the face in box d.
        shape = sp(img, d)
            # Draw the face landmarks on the screen so we can see what face is currently being processed.
        if verbose:
            win.clear_overlay()
            win.add_overlay(d)
            win.add_overlay(shape)

        # Compute the 128D vector that describes the face in img identified by
        # shape.  In general, if two face descriptor vectors have a Euclidean
        # distance between them less than 0.6 then they are from the same
        # person, otherwise they are from different people. Here we just print
        # the vector to the screen.
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        return face_descriptor
        # It should also be noted that you can also call this function like this:
        #  face_descriptor = facerec.compute_face_descriptor(img, shape, 100)
        # The version of the call without the 100 gets 99.13% accuracy on LFW
        # while the version with 100 gets 99.38%.  However, the 100 makes the
        # call 100x slower to execute, so choose whatever version you like.  To
        # explain a little, the 3rd argument tells the code how many times to
        # jitter/resample the image.  When you set it to 100 it executes the
        # face descriptor extraction 100 times on slightly modified versions of
        # the face and returns the average result.  You could also pick a more
        # middle value, such as 10, which is only 10x slower but still gets an
        # LFW accuracy of 99.3%.


        dlib.hit_enter_to_continue()

# Here we use OpenCV to read an image from the camera, save it to a file, and
# return the path to the file. The argument known is a boolean type value.
# getimage(True) - Captures an image and saves it to the known faces folder
# getimage(False) - Captures an image and saves it to the unknown faces folder
def getimage(known):
    if not os.path.isdir(faces_folder_path):
        os.mkdir(faces_folder_path)
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if verbose: cv2.imshow("Capture", frame)
    if known == True:
        img_name = faces_folder_path + "{}.jpg".format(str(time.time()))
    elif known == False:
        if not os.path.isdir(ufaces_folder_path):
            os.mkdir(ufaces_folder_path)
        img_name = ufaces_folder_path + "{}.jpg".format(str(time.time()))
    cv2.imwrite(img_name, frame)
    if verbose: print("{} written!".format(img_name))
    cam.release()
    cv2.destroyAllWindows()
    return img_name

# Here we take the two images (known and unknown) and see if the Euclidian
# Distance is less or more than 0.6
# If Euclidian Distance > 0.6 returns False
# If Euclidian Distance < 0.6 returns True
def login_check():
    unknown = getimage(False)
    count = 0
    threshold = 0.6
    result = 0
    for kface in os.listdir(faces_folder_path):
        known = get_face_desc(faces_folder_path + kface)
        new = get_face_desc(unknown)

        # Check if no face was found
        if type(new) is type(None):
            if verbose: print("No face found. Please try again.")
            return False

        result = get_euc_dist(known,new)
        if result < threshold: break

    return result < threshold

if len(sys.argv) > 1:
    if sys.argv[1] == "-l":
        if login_check() == False:
            print("Failed to get a matching face value. Exiting with Error Code 1...")
            sys.exit(1)  # Return exit code 1 if the facial recognition fails
        print("Face Value Accepted")
        sys.exit(0)
    elif sys.argv[1] != "-l":
        print("Wrong argument given: {}".format(sys.argv[1]))
        print("Use -l for facial comparison check, give no arguments for adding a new known image")

newimg = getimage(True)
print("{} Saved!".format(newimg))
