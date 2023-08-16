import cv2
import time
import glob
import os
from emailling import send_email
from threading import Thread


# Starting the video from the webcam using the laptop's camera.
video = cv2.VideoCapture(0)
# I avoid the black frame at the beginning by giving the camera 1 second to load. Meaning that I create the first
# frame only after waiting for 1 second.
time.sleep(2)

first_frame = None
# This list will be needed later for detecting when the object left the frame.
status_list = []
count = 1


# This function removes all the images from the 'images' folder, which is needed after every time the user exit the
# video.
def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)


while True:
    # This variable set to '0' indicates that there is no object detected in the frame yet.
    status = 0
    # Reading every single frame (image) of the video.
    check, frame = video.read()
    # Changing all the frame's pixels to gray pixels in order to make the frame's
    # comparisons later easier (since the blue, green, red color aren't needed for that).
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Blurring the gray frame to the amount of '(21,21), 0' blurness, because we don't
    # need all that precision.
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)


    # The object detection algorithm:
    # Saving only the first frame in a variable so that we could compare it later with the next frames.
    if first_frame is None:
        first_frame = gray_frame_gau

    # Checking the difference between the first frame and the next frame and saving it (the image result) in a variable.
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
    # Changing all the pixels in the 'delta_frame' image that have a value of 60 or more to the
    # 255 value (white color), in order to emphasize the object popped in the image, and extracting the second item of
    # the list we get - which is the image.
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    # Removing (deleting) all the noise in the image ('thresh_frame'). (Arguments explanation: 'None' as the
    # configuration array. 'iterations=2' the num of processing applied to that method.
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    # Showing (displaying) the thresh-frame (image) on the screen.
    cv2.imshow("My video", dil_frame)

    # Finding the contours of all the objects in the 'dil_frame' image, and saving them in a list named 'contours'.
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Checking all the contours of the objects and if the area of a contour (an object) is less than 5000, then
    # it's not a real object but a light difference or something insignificant between the first frame and the current
    # frame  so continue to the while loop (to the next frame).
    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        # If it's a real object then we extract the coordinates, width and height of the rectangle of the contour.
        x, y, w, h = cv2.boundingRect(contour)
        # Drawing a rectangle around the original frame. '(x,y)' is one point in the rectangle and '(x+w, y+h)' is the
        # second point in the rectangle. '(0, 255, 0)' setting the color of the rectangle to green. Setting the width of
        # the rectangle to '3'.
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        # If we notice a rectangle (a real object) in the view (frame), then update the status to 1.
        if rectangle.any():
            status = 1
            # Saving evey single frame as an image in the 'images' folder, in order to send the best frame in the email.
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1
            # Choosing the image that is in the middle of the 'images' folder.
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    status_list.append(status)
    # Since we only need the 2 last items in the list to detect a change in the statuses' serie, so we update the
    # list and in that way we'll have a small list of 2 items for each frame.
    status_list = status_list[-2:]
    # If the first item in the list is 1 and second is 0, then it means that the object just left the view, so send
    # an email alert.
    if status_list[0] == 1 and status_list[1] == 0:
        # Sending the path of the image to the func by creating a thread object of the 'Thread()' class, because the
        # email being sent and the camera being still on capturing new frames are two threads happening at the same
        # time. 'target' - is the func that will be called by the thread. 'args' - are the arguments of that func.
        email_thread = Thread(target=send_email, args=(image_with_object, ))
        # Activating the 'send_email()' func in the background.
        email_thread.daemon = True
        # Creating a thread for cleaning the folder as well and activating it.
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True
        # Starting the email thread and not the clean thread because otherwise some of the 'images' content will be
        # removed before the email had enough time to send it's content.
        email_thread.start()

    print(status_list)

    cv2.imshow("Video", frame)
    # Creating a keyboard object called 'key'.
    key = cv2.waitKey(1)
    # If the user press 'q' while the mouse is on the video, then it'll break and the video
    # will be released (will stop).
    if key == ord("q"):
        break

# Releasing (stopping) the video.
video.release()
# Cleaning the 'images' only once the user exit the video.
clean_thread.start()

